from django.conf import settings
import tornado.web
import tornado.websocket

from cabbie.apps.drive.location.auth import Authenticator
from cabbie.apps.drive.location.driver import DriverManager
from cabbie.apps.drive.location.proxy import RideProxyManager
from cabbie.apps.drive.location.session import SessionManager
from cabbie.apps.drive.location.watch import WatchManager
from cabbie.utils import json
from cabbie.utils.ioloop import start
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

    def ride_proxy():
        def fget(self):
            return self._ride_proxy
        def fset(self, value):
            self._ride_proxy = value
        return locals()
    ride_proxy = property(**ride_proxy())

    def open(self):
        self.debug('Opened')

    def on_close(self):
        if self.authenticated:
            SessionManager().remove(self._user_id)
        self.debug('Closed')

    def on_message(self, message):
        if not isinstance(message, unicode):
            message = message.decode('utf-8')
        as_json = json.loads(message)
        #self.debug(u'Received: {0}'.format(as_json))

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

    # Driver-side
    # -----------

    def handle_driver_update_location(self, location, charge_type):
        #self.debug('Updating location to {0} (charge_type: {1})'.format(
            #location, charge_type))

        if self.ride_proxy:
            # If there is already ride match, just forward the location info to
            # passenger
            self.ride_proxy.update_driver_location(location)
        else:
            # Otherwise, report to the location manager
            DriverManager().update_location(self._user_id, location,
                                            charge_type)

    def handle_driver_deactivate(self):
        self.info('Deactivated')
        DriverManager().deactivate(self._user_id)

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

    def handle_driver_complete(self, summary):
        self.info('Completed')
        self.ride_proxy.complete(summary)

    def notify_driver_request(self, passenger, source, destination):
        self.send('driver_requested', {
            'passenger': passenger,
            'source': source,
            'destination': destination,
        })

    def notify_driver_cancel(self):
        self.send('driver_canceled')

    def notify_driver_disconnect(self):
        self.send('driver_disconnected')

    # Passenger-side
    # --------------

    def handle_passenger_watch(self, location, charge_type):
        self.info('Watched')
        WatchManager().watch(self._user_id, location, charge_type=charge_type)

    def handle_passenger_unwatch(self):
        self.info('Unwatched')
        WatchManager().unwatch(self._user_id)

    def handle_passenger_request(self, driver_id, source, destination):
        self.info('Requested')

        # Fetch the last driver info before deactivating
        driver_location = DriverManager().get_driver_location(driver_id)

        # Check if driver location is valid
        if not driver_location:
            self.notify_passenger_reject('late')     
            return

        driver_charge_type = DriverManager().get_driver_charge_type(driver_id)

        # Change the states of drivers and passengers accordingly
        WatchManager().unwatch(self._user_id)
        DriverManager().deactivate(driver_id)

        # Create a new ride proxy instance
        proxy = RideProxyManager().create(self._user_id, source, destination)
        proxy.set_driver(driver_id, driver_location, driver_charge_type)
        proxy.request()

    def handle_passenger_cancel(self):
        self.info('Cancelled')
        self.ride_proxy.cancel()

    def notify_passenger_assign(self, assignment):
        if assignment:
            self.debug('Notifying assignment ({0} candidates)'.format(
                len(assignment['candidates'])))
        else:
            self.debug('Notifying empty assignment')

        self.send('passenger_assigned', {'assignment': assignment})

    def notify_passenger_approve(self):
        self.send('passenger_approved')

    def notify_passenger_reject(self, reason):
        self.send('passenger_rejected', {'reason': reason})

    def notify_passenger_progress(self, location, estimate):
        self.send('passenger_progress', {
            'location': location,
            'estimate': estimate,
        })

    def notify_passenger_arrive(self):
        self.send('passenger_arrived')

    def notify_passenger_board(self):
        self.send('passenger_boarded')

    def notify_passenger_journey(self, location, journey):
        self.send('passenger_journey', {
            'location': location,
            'journey': journey,
        })

    def notify_passenger_complete(self, summary, ride_id):
        self.send('passenger_completed', {
            'ride_id': ride_id,
            'summary': summary
        })

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
