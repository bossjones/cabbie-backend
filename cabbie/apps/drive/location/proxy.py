from cabbie.utils.log import LoggableMixin

from cabbie.apps.drive.location.model import ModelManager
from cabbie.apps.drive.location.session import SessionManager
from cabbie.apps.drive.models import Ride


class RideProxy(LoggableMixin):
    """Proxy of `Ride` model for asynchronous save operation and session
    management."""

    # TODO: Periodic calculation of estimated time and distance using
    # TmapEstimator

    def __init__(self, passenger_id, location):
        super(RideProxy, self).__init__()
        self._passenger_id = passenger_id
        self._passenger_location = location
        self._driver_id = None
        self._state = None

        self.passenger_session.ride_proxy = self

    @property
    def driver(self):
        return ModelManager().get_driver(self._driver_id)

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
        self._driver_id = driver_id
        self.driver_session.ride_proxy = self

    def reset_driver(self):
        self.driver_session.ride_proxy = None
        self._driver_id = None

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
        pass

    def driver_rate(self, rating, comment):
        # FIXME: Syncing to DB
        self.reset_driver()

    def _transition_to(self, state):
        self.info('Transiting from `{old}` to `{new}`'.format(
            old=self._state, new=state))
        self._state = state
        # FIXME: Syncing to DB

