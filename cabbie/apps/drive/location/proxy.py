from tornado import gen

from cabbie.apps.drive.location.model import ModelManager
from cabbie.apps.drive.location.secret import fetch
from cabbie.apps.drive.location.session import SessionManager
from cabbie.apps.drive.models import Ride
from cabbie.utils.log import LoggableMixin
from cabbie.utils.meta import SingletonMixin
from cabbie.utils.pubsub import PubsubMixin


class RideProxy(LoggableMixin, PubsubMixin):
    """Proxy of `Ride` model for asynchronous save operation and session
    management."""

    create_path = '/_/drive/ride/create'
    update_path = '/_/drive/ride/{pk}/update'

    def __init__(self, passenger_id, source, destination):
        super(RideProxy, self).__init__()
        self._passenger_id = passenger_id
        self._passenger_location = None
        self._source = source
        self._destination = destination
        self._driver_id = None
        self._driver_location = None
        self._driver_charge_type = None
        self._state = None
        self._ride_id = None
        self._update_queue = []

        # Passenger location is not updated periodically so just use the source
        # location instead
        self._passenger_location = self._source.get('location')

        self.passenger_session.ride_proxy = self

    @property
    def driver(self):
        return (ModelManager().get_driver(self._driver_id)
                if self._driver_id else None)

    @property
    def passenger(self):
        return ModelManager().get_passenger(self._passenger_id)

    @property
    def driver_session(self):
        return SessionManager().get(self._driver_id)

    @property
    def passenger_session(self):
        return SessionManager().get(self._passenger_id)

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

    # State methods
    # -------------

    def request(self):
        self.driver_session.notify_driver_request(**{
            'passenger': ModelManager().get_passenger(self._passenger_id),
            'source': self._source,
            'destination': self._destination,
        })
        self._transition_to(Ride.REQUESTED, update=False)
        self._create(source=self._source, destination=self._destination)

    def cancel(self):
        self.driver_session.notify_driver_cancel()
        self._transition_to(Ride.CANCELED)
        self._reset_driver()

    def approve(self):
        self.passenger_session.notify_passenger_approve()
        self._transition_to(Ride.APPROVED)

    def reject(self, reason):
        self.passenger_session.notify_passenger_reject(reason)
        self._transition_to(Ride.REJECTED, reason=reason)
        self._reset_driver()

    def progress(self, location):
        # TODO: Periodic calculation of estimated time and distance using
        # TmapEstimator
        self._driver_location = location
        if self.passenger_session:
            self.passenger_session.notify_passenger_progress(location)

    def arrive(self):
        self.passenger_session.notify_passenger_arrive()
        self._transition_to(Ride.ARRIVED)

    def board(self):
        self.passenger_session.notify_passenger_board()
        self._transition_to(Ride.BOARDED)

    def complete(self, summary):
        self.passenger_session.notify_passenger_complete(summary)
        self._transition_to(Ride.COMPLETED, summary=summary)
        self._reset_driver()

    def passenger_rate(self, rating, ratings_by_category, comment):
        self._transition_to(Ride.RATED, rating=rating,
                            ratings_by_category=ratings_by_category,
                            comment=comment)
        self.publish('finished', self)

    def passenger_disconnect(self):
        if self.driver_session:
            self.driver_session.notify_driver_disconnect()
            self.driver_session.ride_proxy = None
        self._transition_to(Ride.DISCONNECTED, sinner='passenger')
        self.publish('finished', self)

    def driver_disconnect(self):
        if self.passenger_session:
            self.passenger_session.notify_passenger_disconnect()
        self._transition_to(Ride.DISCONNECTED, sinner='driver')
        self._reset_driver()

    def _transition_to(self, state, update=True, **kwargs):
        self.info('Transiting from `{old}` to `{new}`'.format(
            old=self._state, new=state))
        self._state = state
        if update:
            self._update(**kwargs)

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
    def __init__(self):
        super(RideProxyManager, self).__init__()
        self._proxies_by_passenger = {}
        self._proxies_by_driver = {}

        SessionManager().subscribe('passenger_closed',
                                   self.on_passenger_session_closed)
        SessionManager().subscribe('driver_closed',
                                   self.on_driver_session_closed)

    def create(self, passenger_id, source, destination):
        proxy = RideProxy(passenger_id, source, destination)
        proxy.subscribe('driver_set', self.on_ride_proxy_driver_set)
        proxy.subscribe('driver_resetted', self.on_ride_proxy_driver_resetted)
        proxy.subscribe('finished', self.on_ride_proxy_finished)
        self._proxies_by_passenger[passenger_id] = proxy
        return proxy

    def on_ride_proxy_driver_set(self, ride_proxy, driver_id):
        self._proxies_by_driver[driver_id] = ride_proxy

    def on_ride_proxy_driver_resetted(self, ride_proxy, old_driver_id):
        self._proxies_by_driver.pop(old_driver_id, None)

    def on_ride_proxy_finished(self, ride_proxy):
        driver = ride_proxy.driver
        if driver:
            self._proxies_by_driver.pop(driver['id'], None)
        self._proxies_by_passenger.pop(ride_proxy.passenger['id'], None)

    def on_passenger_session_closed(self, user_id, old_session):
        proxy = self._proxies_by_passenger.pop(user_id, None)
        if proxy:
            proxy.passenger_disconnect()

    def on_driver_session_closed(self, user_id, old_session):
        proxy = self._proxies_by_driver.pop(user_id, None)
        if proxy:
            proxy.driver_disconnect()
