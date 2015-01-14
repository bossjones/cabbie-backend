import time
from functools import partial

from django.conf import settings
from tornado import gen

from cabbie.apps.drive.location.estimate import HaversineEstimator
from cabbie.apps.drive.location.model import ModelManager
from cabbie.apps.drive.location.secret import fetch
from cabbie.apps.drive.location.session import SessionManager, SessionBufferManager
from cabbie.apps.drive.models import Ride
from cabbie.utils.geo import distance
from cabbie.utils.ioloop import delay, cancel
from cabbie.utils.log import LoggableMixin
from cabbie.utils.meta import SingletonMixin
from cabbie.utils.pubsub import PubsubMixin


class RideProxy(LoggableMixin, PubsubMixin):
    """Proxy of `Ride` model for asynchronous save operation and session
    management."""

    create_path = '/_/drive/ride/create'
    update_path = '/_/drive/ride/{pk}/update'
    refresh_interval = settings.RIDE_ESTIMATE_REFRESH_INTERVAL

    def __init__(self, passenger_id, source, destination, additional_message):
        super(RideProxy, self).__init__()
        self._passenger_id = passenger_id
        self._passenger_location = None
        self._source = source
        self._destination = destination
        self._additional_message = additional_message 

        self._driver_id = None
        self._driver_location = None
        self._driver_charge_type = None
        self._state = None
        self._ride_id = None
        self._update_queue = []

        self._estimate = None
        self._journey = None
        self._boarded_at = None
        self._boarded_location = None

        # Passenger location is not updated periodically so just use the source
        # location instead
        self._passenger_location = self._source.get('location')

        self.passenger_session.ride_proxy = self

        # timeout callback
        self._timeout_reject = None

    def __unicode__(self):
        return u'RideProxy(P-{0}-D-{1} {2} R-{3})'.format(self._passenger_id, 
                                        self._driver_id, self._state, self._ride_id)

    @property
    def driver(self):
        return (ModelManager().get_driver(self._driver_id)
                if self._driver_id else None)

    @property
    def passenger(self):
        return (ModelManager().get_passenger(self._passenger_id)
                if self._passenger_id else None)

    @property
    def driver_session(self):
        driver_session = SessionManager().get(self._driver_id)
        #return driver_session
        return driver_session if driver_session else SessionBufferManager().get_or_create(self._driver_id)

    @property
    def passenger_session(self):
        passenger_session = SessionManager().get(self._passenger_id)
        #return passenger_session
        return passenger_session if passenger_session else SessionBufferManager().get_or_create(self._passenger_id)

    def set_driver(self, driver_id, location, charge_type):
        self.debug('Setting driver to {0}'.format(driver_id))
        self._driver_id = driver_id
        self._driver_location = location
        self._driver_charge_type = charge_type
        self.driver_session.ride_proxy = self
        self.publish('driver_set', self, driver_id)

    def _reset_driver(self):
        self.debug('Resetting driver')
        old_driver_id = self._driver_id
        if self.driver_session:
            self.driver_session.ride_proxy = None
        self._driver_id = None
        self.publish('driver_resetted', self, old_driver_id)

    def _reset_passenger(self):
        self.debug('Resetting passenger')
        old_passenger_id = self._passenger_id
        if self.passenger_session:
            self.passenger_session.ride_proxy = None
        self._passenger_id = None
        self.publish('passenger_resetted', self, old_passenger_id)


    # State methods
    # -------------

    def request(self):
        self.driver_session.notify_driver_request(**{
            'passenger': ModelManager().get_passenger(self._passenger_id),
            'source': self._source,
            'destination': self._destination,
            'additional_message': self._additional_message,
        })
        self._transition_to(Ride.REQUESTED, update=False)
        self._create(source=self._source, destination=self._destination, additional_message=self._additional_message)

        # timeout 30s
        self._timeout_reject = delay(settings.REQUEST_TIMEOUT, partial(self.reject, 'timeout'))

    def _cancel_timeout_reject(self):
        self.info('Cancel reject timeout')
        cancel(self._timeout_reject)

    def cancel(self):
        # cancel timed out reject
        self._cancel_timeout_reject()

        self.driver_session.notify_driver_cancel()
        self._transition_to(Ride.CANCELED)
        self._reset_driver()
        self._reset_passenger()

    def approve(self):
        # cancel timed out reject
        self._cancel_timeout_reject()

        self.passenger_session.notify_passenger_approve()
        self._transition_to(Ride.APPROVED)

        # Start periodic refreshing
        self._refresh_estimate()

    def reject(self, reason):
        # cancel timed out reject
        self._cancel_timeout_reject()

        self.passenger_session.notify_passenger_reject(reason)
        self._transition_to(Ride.REJECTED, reason=reason)
        self._reset_driver()
        self._reset_passenger()

    def arrive(self):
        # cancel timed out reject
        self._cancel_timeout_reject()

        self.passenger_session.notify_passenger_arrive()
        self._transition_to(Ride.ARRIVED)

    def board(self):
        # cancel timed out reject
        self._cancel_timeout_reject()

        self.passenger_session.notify_passenger_board()
        self._transition_to(Ride.BOARDED)

        self._boarded_at = time.time()
        self._boarded_location = self._driver_location

    def complete(self, summary):
        # cancel timed out reject
        self._cancel_timeout_reject()

        self.passenger_session.notify_passenger_complete(summary, self._ride_id)
        self._transition_to(Ride.COMPLETED, summary=summary)
        self._reset_driver()
        self._reset_passenger()

    def update_driver_location(self, location):
        self._driver_location = location

        if self._state == Ride.APPROVED:
            self.passenger_session.notify_passenger_progress(
                self._driver_location, self._estimate)

        elif self._state == Ride.BOARDED:
            self._journey = {
                'time': time.time() - self._boarded_at,
                'distance': distance(self._driver_location,
                                     self._boarded_location),
            }
            self.passenger_session.notify_passenger_journey(
                self._driver_location, self._journey)

    def passenger_rate(self, rating, ratings_by_category, comment):
        self._transition_to(Ride.RATED, rating=rating,
                            ratings_by_category=ratings_by_category,
                            comment=comment)
        self.publish('finished', self)

    def passenger_disconnect(self):
        # cancel timed out reject
        self._cancel_timeout_reject()

        if self.driver_session:
            self.driver_session.notify_driver_disconnect()
            self.driver_session.ride_proxy = None
        self.publish('finished', self)

    def driver_disconnect(self):
        # cancel timed out reject
        self._cancel_timeout_reject()

        if self.passenger_session:
            self.passenger_session.notify_passenger_disconnect()
        self._reset_driver()

    def _transition_to(self, state, update=True, **kwargs):
        self.info('Transiting from `{old}` to `{new}`'.format(
            old=self._state, new=state))
        self._state = state
        if update:
            self._update(**kwargs)

    # Estimate
    # --------

    @gen.coroutine
    def _refresh_estimate(self):
        if self._state != Ride.APPROVED:
            return

        self._estimate = yield HaversineEstimator().estimate(
            self._driver_location, self._passenger_location)

        delay(self.refresh_interval, self._refresh_estimate)

    # Sync
    # ----

    def _common(self):
        return {
            'passenger_id': self._passenger_id,
            'passenger_location': self._passenger_location,
            'driver_id': self._driver_id,
            'driver_location': self._driver_location,
            'state': self._state,
            'charge_type': self._driver_charge_type,
        }

    @gen.coroutine
    def _create(self, **kwargs):
        data = self._common()
        data.update(kwargs)
        payload = yield fetch(self.create_path, data)
        if payload['status'] != 'success':
            self.error('Failed to create a ride entry')
        else:
            self._ride_id = payload['data']['id']

    @gen.coroutine
    def _update(self, **kwargs):
        data = self._common()
        data.update(kwargs)
        self._update_queue.append(data)

        if self._ride_id:
            url = self.update_path.format(pk=self._ride_id)
            while self._update_queue:
                yield fetch(url, self._update_queue.pop(0))

class RideProxyManager(LoggableMixin, SingletonMixin):

    disconnectable_state = [Ride.REQUESTED]

    def __init__(self):
        super(RideProxyManager, self).__init__()
        self._proxies_by_passenger = {}
        self._proxies_by_driver = {}

        SessionManager().subscribe('passenger_closed',
                                   self.on_passenger_session_closed)
        SessionManager().subscribe('driver_closed',
                                   self.on_driver_session_closed)

    def create(self, passenger_id, source, destination, additional_message):
        proxy = RideProxy(passenger_id, source, destination, additional_message)
        proxy.subscribe('driver_set', self.on_ride_proxy_driver_set)
        proxy.subscribe('driver_resetted', self.on_ride_proxy_driver_resetted)
        proxy.subscribe('passenger_resetted', self.on_ride_proxy_passenger_resetted)
        proxy.subscribe('finished', self.on_ride_proxy_finished)
        self._proxies_by_passenger[passenger_id] = proxy
        return proxy

    def get_ride_proxy_by_driver_id(self, driver_id):
        return self._proxies_by_driver.get(driver_id, None)

    def get_ride_proxy_by_passenger_id(self, passenger_id):
        return self._proxies_by_passenger.get(passenger_id, None)

    def on_ride_proxy_driver_set(self, ride_proxy, driver_id):
        self._proxies_by_driver[driver_id] = ride_proxy

    def on_ride_proxy_driver_resetted(self, ride_proxy, old_driver_id):
        self._proxies_by_driver.pop(old_driver_id, None)

    def on_ride_proxy_passenger_resetted(self, ride_proxy, old_passenger_id):
        #self._proxies_by_passenger.pop(old_passenger_id, None)
        pass

    def on_ride_proxy_finished(self, ride_proxy):
       #driver = ride_proxy.driver
       #if driver:
       #    self._proxies_by_driver.pop(driver['id'], None)
       #self._proxies_by_passenger.pop(ride_proxy.passenger['id'], None)
        pass

    def on_passenger_session_closed(self, user_id, old_session):
        self.debug('Passenger {0} session closed'.format(user_id))

        proxy = self._proxies_by_passenger.get(user_id, None)

        # notify to self
        old_session.notify_passenger_disconnect()            

        # notify to counterpart
        if proxy:
            #proxy.passenger_disconnect()
            pass



    def on_driver_session_closed(self, user_id, old_session):
        self.debug('Driver {0} session closed'.format(user_id))

        proxy = self._proxies_by_driver.pop(user_id, None)

        #notify to self
        old_session.notify_driver_disconnect()

        # REQUESTED, APPROVED, ARRIVED
        if proxy and proxy._state in self.disconnectable_state:
            proxy.driver_disconnect()
