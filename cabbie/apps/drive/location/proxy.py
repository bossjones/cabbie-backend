from cabbie.apps.drive.location.model import ModelManager
from cabbie.apps.drive.location.session import SessionManager
from cabbie.apps.drive.models import Ride
from cabbie.utils.log import LoggableMixin
from cabbie.utils.meta import SingletonMixin
from cabbie.utils.pubsub import PubsubMixin


class RideProxy(LoggableMixin, PubsubMixin):
    """Proxy of `Ride` model for asynchronous save operation and session
    management."""

    def __init__(self, passenger_id, location):
        super(RideProxy, self).__init__()
        self._passenger_id = passenger_id
        self._passenger_location = location
        self._driver_id = None
        self._state = None

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

    def set_driver(self, driver_id):
        self.debug('Setting driver to {0}'.format(driver_id))
        self._driver_id = driver_id
        self.driver_session.ride_proxy = self
        self.publish('driver_set', self, driver_id)

    def reset_driver(self):
        self.debug('Resetting driver')
        old_driver_id = self._driver_id
        if self.driver_session:
            self.driver_session.ride_proxy = None
        self._driver_id = None
        self.publish('driver_resetted', self, old_driver_id)

    def request(self):
        self.driver_session.notify_driver_request(**{
            'passenger': ModelManager().get_passenger(self._passenger_id),
            'location': self._passenger_location,
        })
        self._transition_to(Ride.REQUESTED)

    def cancel(self):
        self.driver_session.notify_driver_cancel()
        self._transition_to(Ride.CANCELED)
        self.reset_driver()

    def approve(self):
        self.passenger_session.notify_passenger_approve()
        self._transition_to(Ride.APPROVED)

    def reject(self, reason):
        self.passenger_session.notify_passenger_reject(reason)
        self._transition_to(Ride.REJECTED)
        self.reset_driver()

    def progress(self, location):
        # TODO: Periodic calculation of estimated time and distance using
        # TmapEstimator
        if self.passenger_session:
            self.passenger_session.notify_passenger_progress(location)

    def arrive(self):
        self.passenger_session.notify_passenger_arrive()
        self._transition_to(Ride.ARRIVED)

    def board(self):
        self.passenger_session.notify_passenger_board()
        self._transition_to(Ride.BOARDED)

    def complete(self):
        self.passenger_session.notify_passenger_complete()
        self._transition_to(Ride.COMPLETED)

    def passenger_rate(self, rating, comment):
        # FIXME: Syncing to DB
        self.publish('finished', self)

    def driver_rate(self, rating, comment):
        # FIXME: Syncing to DB
        self.reset_driver()

    def passenger_disconnect(self):
        self.driver_session.notify_driver_disconnect()
        self.driver_session.ride_proxy = None
        self.publish('finished', self)

    def driver_disconnect(self):
        self.passenger_session.notify_passenger_disconnect()
        self.reset_driver()

    def _transition_to(self, state):
        self.info('Transiting from `{old}` to `{new}`'.format(
            old=self._state, new=state))
        self._state = state
        # FIXME: Syncing to DB


class RideProxyManager(LoggableMixin, SingletonMixin):
    def __init__(self):
        super(RideProxyManager, self).__init__()
        self._proxies_by_passenger = {}
        self._proxies_by_driver = {}

        SessionManager().subscribe('passenger_closed',
                                   self.on_passenger_session_closed)
        SessionManager().subscribe('driver_closed',
                                   self.on_driver_session_closed)

    def create(self, passenger_id, location):
        proxy = RideProxy(passenger_id, location)
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
