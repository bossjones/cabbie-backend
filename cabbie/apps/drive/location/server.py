from django.conf import settings
import tornado.web
import tornado.websocket

from cabbie.apps.drive.location.auth import Authenticator
from cabbie.apps.drive.location.geo import LocationManager
from cabbie.apps.drive.location.loop import start
from cabbie.apps.drive.location.proxy import RideProxy
from cabbie.apps.drive.location.session import SessionManager
from cabbie.apps.drive.location.watch import WatchManager
from cabbie.utils import json
from cabbie.utils.log import LoggableMixin
from cabbie.utils.meta import SingletonMixin


# Handler
# -------

class Session(LoggableMixin, tornado.websocket.WebSocketHandler):
    """Represents a (web)socket session of driver or passenger."""

    def __init__(self, *args, **kwargs):
        super(Session, self).__init__(*args, **kwargs)
        self._user_id = None
        self._role = None
        self._ride_proxy = None

    def __unicode__(self):
        return (u'Session({role}-{id})'.format(role=self._role[0].upper(),
                                               id=self._user_id)
                if self.authenticated else u'Session')

    @property
    def authenticated(self):
        return self._user_id is not None

    @property
    def role(self):
        return self._role

    def open(self):
        self.debug('Opened')

    def on_close(self):
        if self.authenticated:
            SessionManager().remove(self._user_id)
        self.debug('Closed')

    def on_message(self, message):
        as_json = json.loads(message)
        self.debug('Received: {0}'.format(as_json))

        method = as_json['type']
        data = as_json.get('data', {})

        # Check permission
        if method != 'auth' and not self.authenticated:
            self.send_error('Authentication required')
            return

        # FIXME: Handle exceptions
        getattr(self, 'handle_{method}'.format(method=method))(**data)

    # Utils
    # -----

    def send(self, type, data=None):
        self.write_message(json.dumps({'type': type, 'data': data or {}}))

    def send_error(self, error_msg=None):
        self.send('error', {'msg': error_msg or ''})

    # Common
    # ------

    def handle_auth(self, token, role):
        user_id = Authenticator().authenticate(token, role)

        if not user_id:
            self.warn('Failed to authenticate: {0}'.format(token))
            self.send_error('Failed to authenticate')
            return

        self._user_id = user_id
        self._role = role
        SessionManager().add(user_id, self)

        self.info('{role} {id} was authenticated'.format(
            role=role.capitalize(), id=user_id))

        self.send('auth_succeeded')

    def ride_proxy():
        def fget(self):
            return self._ride_proxy
        def fset(self, value):
            self._ride_proxy = value
        return locals()
    ride_proxy = property(**ride_proxy())

    # Driver-side
    # -----------

    def handle_driver_update_location(self, location):
        self.debug('Updating location to {0}'.format(location))

        if self.ride_proxy:
            # If there is already ride match, just forward the location info to
            # passenger
            self.ride_proxy.progress(location)
        else:
            # Otherwise, report to the location manager
            LocationManager().update_location(self._user_id, location)

    def handle_driver_deactivate(self):
        self.info('Deactivated')
        LocationManager().deactivate(self._user_id)

    def handle_driver_approve(self):
        self.info('Approved')
        self.ride_proxy.approve()

    def handle_driver_reject(self, reason):
        self.info('Rejected')
        self.ride_proxy.reject(reason)

    def handle_driver_arrive(self):
        self.info('Arrived')
        self.ride_proxy.arrive()

    def handle_driver_board(self):
        self.info('Boarded')
        self.ride_proxy.board()

    def handle_driver_complete(self):
        self.info('Completed')
        self.ride_proxy.complete()

    def handle_driver_rate(self, rating, comment):
        self.info('Rated')
        self.ride_proxy.driver_rate(rating, comment)

    def notify_driver_request(self, passenger, location):
        self.send('driver_requested', {
            'passenger': passenger,
            'location': location
        })

    def notify_driver_cancel(self):
        self.send('driver_canceled')

    def notify_driver_disconnect(self):
        self.send('driver_disconnected')

    # Passenger-side
    # --------------

    def handle_passenger_watch(self, location):
        self.info('Watched')
        WatchManager().watch(self._user_id, location)

    def handle_passenger_request(self, driver_id, location):
        self.info('Requested')

        # Change the states of drivers and passengers accordingly
        WatchManager().unwatch(self._user_id)
        LocationManager().deactivate(driver_id)

        # Create a new ride proxy instance
        proxy = RideProxy(self._user_id, location)
        proxy.set_driver(driver_id)
        proxy.request()

    def handle_passenger_cancel(self):
        self.info('Cancelled')
        self.ride_proxy.cancel()

    def handle_passenger_rate(self, rating, comment):
        self.info('Rated')
        self.ride_proxy.passenger_rate(rating, comment)

    def notify_passenger_assign(self, assignment):
        self.debug('Notifying new assignment: {0}'.format(assignment))
        self.send('passenger_assigned', {
            'assignment': assignment,
        })

    def notify_passenger_approve(self):
        self.send('passenger_approved')

    def notify_passenger_reject(self, reason):
        self.send('passenger_rejected', {'reason': reason})

    def notify_passenger_progress(self, location):
        self.send('passenger_progress', {
            'location': location,
        })

    def notify_passenger_arrive(self):
        self.send('passenger_arrived')

    def notify_passenger_board(self):
        self.send('passenger_boarded')

    def notify_passenger_complete(self):
        self.send('passenger_completed')

    def notify_passenger_disconnect(self):
        self.send('passenger_disconnected')


# Server
# ------

class LocationServer(LoggableMixin, SingletonMixin):
    def start(self):
        application = tornado.web.Application([
            (r'/location', Session),
        ])
        application.listen(settings.LOCATION_SERVER_PORT)

        self.info('Start serving')

        start()
