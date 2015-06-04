from django.conf import settings
from django.db.models import Q

import tornado.web
import tornado.websocket

from cabbie.apps.drive.models import Ride
from cabbie.apps.drive.location.auth import Authenticator
from cabbie.apps.drive.location.driver import DriverManager
from cabbie.apps.drive.location.proxy import RideProxyManager
from cabbie.apps.drive.location.request import RequestProxyManager
from cabbie.apps.drive.location.session import SessionManager, SessionBufferManager
from cabbie.apps.drive.location.watch import WatchManager
from cabbie.utils import json
from cabbie.utils.ioloop import start, delay
from cabbie.utils.log import LoggableMixin
from cabbie.utils.meta import SingletonMixin
from cabbie.utils.pubsub import PubsubMixin

# Handler
# -------

class Session(LoggableMixin, PubsubMixin, tornado.websocket.WebSocketHandler):
    """Represents a (web)socket session of driver or passenger."""

    heartbeating_interval = 1
    dead_point = 10

    def __init__(self, *args, **kwargs):
        super(Session, self).__init__(*args, **kwargs)
        self._user_id = None
        self._role = None
        self._ride_proxy = None
        self._ping_count = 0

    def _ping(self):
        try:
            self.ping('data')
            self._ping_count += 1
            
        except tornado.websocket.WebSocketClosedError:
            self.info('Closed session {0}, finish ping'.format(hex(id(self))))
            return

        if self._ping_count == self.dead_point:
            self.info('Close session {0} which cannot get pong {1} times'.format(hex(id(self)), self.dead_point))

            if self.authenticated:
                SessionManager().remove(self._user_id, self)
                self.debug('Closed {0}'.format(hex(id(self))))

            self.close();
            return

        delay(self.heartbeating_interval, self._ping)

    def on_pong(self, data):
        # remove session buffer
        self._ping_count -= 1

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
        self.debug('Opened {0}'.format(hex(id(self))))

    def on_close(self):
        if self.authenticated:
            SessionManager().remove(self._user_id, self)
        self.debug('Closed {0}'.format(hex(id(self))))

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
        try:
            self.write_message(json.dumps({'type': type, 'data': data or {}}))
        except tornado.websocket.WebSocketClosedError, e:
            self.info('Closed session {session}, ignore to send message {type}'.format(session=hex(id(self)), type=type))
    

    def send_error(self, error_msg=None):
        self.send('error', {'msg': error_msg or ''})

    # Common
    # ------

    def handle_auth(self, token, role):
        user = Authenticator().authenticate(token, role)

        if not user:
            self.warn('Failed to authenticate: {0}'.format(token))
            self.send_error('Failed to authenticate: cannot find user')
            return

        # driver : check if freezed 
        if role == 'driver':
            driver = user.get_role(role)
            
            if driver.is_freezed:
                self.warn('Failed to authenticate: driver {0} is freezed now'.format(driver))
                self.send_error('Failed to authenticate: freezed')
                return

        self._user_id = user.id
        self._role = role
        SessionManager().add(user.id, self)

        self.info('{role} {id} was authenticated'.format(
            role=role.capitalize(), id=user.id))

        self.send('auth_succeeded')
    
        # link old ride proxy
        if self._role == 'driver':
            old_ride_proxy = RideProxyManager().get_ride_proxy_by_driver_id(self._user_id)
        elif self._role == 'passenger':
            old_ride_proxy = RideProxyManager().get_ride_proxy_by_passenger_id(self._user_id)
        
        if old_ride_proxy and old_ride_proxy._state in [Ride.REQUESTED, Ride.APPROVED, Ride.ARRIVED, Ride.BOARDED]:
            self.debug('Alive old ride proxy found for {0} {1}: {2}'.format(self._role, self._user_id, old_ride_proxy))
            self.ride_proxy = old_ride_proxy
      
        # flush buffered messages
        session_buffer = SessionBufferManager().get_or_create(self._user_id)
        session_buffer.flush(self) 
        SessionBufferManager().remove(self._user_id)

        # start heartbeating
 #       self._ping()

    # Driver-side
    # -----------

    def handle_driver_update_location(self, location, charge_type):

        if self.ride_proxy:
            # If there is already ride match, just forward the location info to
            # passenger
            self.debug('Updating location to {0} to {1}'.format(location, self.ride_proxy.passenger_session))
            self.ride_proxy.update_driver_location(location)
        else:
            # Otherwise, report to the location manager
            #self.debug('Updating location to {0}'.format(location))
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

        if self.ride_proxy:
            self.ride_proxy.reject(reason)
        else: 
            self.info('No proxy, seems already timed out by server')

    def handle_driver_arrive(self):
        self.info('Arrived')
        self.ride_proxy.arrive()

    def handle_driver_board(self):
        self.info('Boarded')
        self.ride_proxy.board()

    def handle_driver_complete(self, summary):
        self.info('Complete, but do not handle')

    def notify_driver_request(self, ride_id, passenger, source, destination, additional_message):
        self.send('driver_requested', {
            'ride_id': ride_id,
            'passenger': passenger,
            'source': source,
            'destination': destination,
            'additional_message': additional_message,
        })

    def notify_driver_cancel(self):
        self.send('driver_canceled')

    def notify_driver_disconnect(self):
        self.send('driver_disconnected')

    # Passenger-side
    # --------------

    def handle_passenger_watch(self, location, charge_type):
        self.info('Watched')
        WatchManager().watch(self._user_id, location, charge_type=charge_type, immediate_assign=False)

    def handle_passenger_unwatch(self):
        self.info('Unwatched')
        WatchManager().unwatch(self._user_id)

    def handle_passenger_request(self, driver_id, charge_type, source, destination, additional_message):
        self.info('Requested')

        # Fetch the last driver info before deactivating
        driver_location = DriverManager().get_driver_location(driver_id)

        # Check if driver location is valid
        if driver_location is None:
            self.notify_passenger_reject('late')     
            return

        driver_charge_type = DriverManager().get_driver_charge_type(driver_id)

        # Check if driver charge type is still valid
        if charge_type != driver_charge_type:
            self.notify_passenger_reject('charge_type mismatch')
            return

        # Change the states of drivers and passengers accordingly
        WatchManager().unwatch(self._user_id)
        DriverManager().deactivate(driver_id)

        # Create a new ride proxy instance
        proxy = RideProxyManager().create(self._user_id, source, destination, additional_message)
        proxy.set_driver(driver_id, driver_location, driver_charge_type)

        # notify to driver
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

    def notify_passenger_board(self, ride_id):
        self.send('passenger_boarded', {
            'ride_id': ride_id,
        })

    def notify_passenger_journey(self, location, journey):
        self.send('passenger_journey', {
            'location': location,
            'journey': journey,
        })

    # deprecated
    def notify_passenger_complete(self, summary, ride_id):
        self.send('passenger_completed', {
            'ride_id': ride_id,
            'summary': summary
        })

    def notify_passenger_disconnect(self):
        self.send('passenger_disconnected')


class SessionBuffer(LoggableMixin):
    """Represents a (web)socket session buffer of driver or passenger."""

    def __init__(self, user_id, *args, **kwargs):
        super(SessionBuffer, self).__init__(*args, **kwargs)
        self._user_id = user_id
        self._buffered = []

    def __unicode__(self):
        return (u'SessionBuffer({id})'.format(id=self._user_id)
                if self.authenticated else u'SessionBuffer')

    @property
    def authenticated(self):
        return self._user_id is not None

    def _buffer(self, method, type, data=None):
        if len(self._buffered) == 0:
            # add first
            self._buffered.append({'method': method, 'type': type, 'data': data or {}})
        elif self._buffered[-1]['method'] == method:
            # update
            self._buffered[-1] = {'method': method, 'type': type, 'data': data or {}}
        else:
            # add
            self._buffered.append({'method': method, 'type': type, 'data': data or {}})
            
        self.debug('Buffer message {0} for user {1}, buffered size {2}'.format(type, self._user_id, len(self._buffered)))

    @property
    def size(self):
        return len(self._buffered)

    def flush(self, session):
        self.debug('Flush buffered message')

        for message in self._buffered:
            self.debug('Flush buffered message {0}'.format(message['type']))
            getattr(session, message['method'])(**message['data'])

    def notify_driver_request(self, ride_id, passenger, source, destination, additional_message):
        self._buffer('notify_driver_request', 'driver_requested', {
            'ride_id': ride_id,
            'passenger': passenger,
            'source': source,
            'destination': destination,
            'additional_message': additional_message,
        })

    def notify_driver_cancel(self):
        self._buffer('notify_driver_cancel', 'driver_canceled')

    def notify_driver_disconnect(self):
        self._buffer('notify_driver_disconnect', 'driver_disconnected')

    # Passenger-side
    # --------------

    def notify_passenger_assign(self, assignment):
        if assignment:
            self.debug('Notifying assignment ({0} candidates)'.format(
                len(assignment['candidates'])))
        else:
            self.debug('Notifying empty assignment')

        self._buffer('notify_passenger_assign', 'passenger_assigned', {'assignment': assignment})

    def notify_passenger_approve(self):
        self._buffer('notify_passenger_approve', 'passenger_approved')

    def notify_passenger_reject(self, reason):
        self._buffer('notify_passenger_reject', 'passenger_rejected', {'reason': reason})

    def notify_passenger_progress(self, location, estimate):
        self._buffer('notify_passenger_progress', 'passenger_progress', {
            'location': location,
            'estimate': estimate,
        })

    def notify_passenger_arrive(self):
        self._buffer('notify_passenger_arrive', 'passenger_arrived')

    def notify_passenger_board(self, ride_id):
        self._buffer('notify_passenger_board', 'passenger_boarded', {
            'ride_id': ride_id,
        })

    def notify_passenger_journey(self, location, journey):
        self._buffer('notify_passenger_journey', 'passenger_journey', {
            'location': location,
            'journey': journey,
        })

    def notify_passenger_complete(self, summary, ride_id):
        self._buffer('notify_passenger_complete', 'passenger_completed', {
            'ride_id': ride_id,
            'summary': summary
        })

    def notify_passenger_disconnect(self):
        self._buffer('notify_passenger_disconnect', 'passenger_disconnected')

# Web
class RideProxyMixin:
    def proxy_by_ride_id(self, ride_id):
        return RideProxyManager().get_ride_proxy_by_ride_id(ride_id)

    def proxy_by_driver_id(self, driver_id):
        return RideProxyManager().get_ride_proxy_by_driver_id(driver_id)


class DriverAuthenticatedWebHandler(tornado.web.RequestHandler):

    driver = None

    def authenticate(self):
        token_header = self.request.headers['Authorization']
        try:
            token = token_header.split(' ')[1]
        except:
            raise tornado.web.HTTPError(401, 'token not found')
        else:
            self.driver = Authenticator().authenticate(token, 'driver')
            
            if self.driver:
                return True
            else:
                raise tornado.web.HTTPError(401, 'driver not authenticated')

    @property
    def is_authenticated(self):
        return self.driver is not None


class PassengerAuthenticatedWebHandler(tornado.web.RequestHandler):

    passenger = None

    def authenticate(self):
        token_header = self.request.headers['Authorization']
        try:
            token = token_header.split(' ')[1]
        except:
            raise tornado.web.HTTPError(401, 'token not found')
        else:
            self.passenger = Authenticator().authenticate(token, 'passenger')
            
            if self.passenger:
                return True
            else:
                raise tornado.web.HTTPError(401, 'passenger not authenticated')

    @property
    def is_authenticated(self):
        return self.passenger is not None


class WebSessionLocation(RideProxyMixin, LoggableMixin, DriverAuthenticatedWebHandler):

    charge_type = 1000  # discard later

    def __unicode__(self):
        return u'WebSessionLocation(D-{id})'.format(id=self.driver.id) if self.is_authenticated else u'WebSessionLocation'

    def get(self):
        self.authenticate()

        self.debug('Getting location of {0} via http'.format(self.driver.id))

        location = DriverManager().get_driver_location(self.driver.id)
        
        if location is None:
            raise tornado.web.HTTPError(403, 'location not found') 

        self.write(json.dumps({ 'location':location }))
    
    def post(self):
        self.authenticate()

        location = self.get_argument('location')

        proxy = self.proxy_by_driver_id(self.driver.id)

        if proxy:
            self.debug('Updating location to {0} to {1} via http'.format(location, proxy.passenger_session))
            proxy.update_driver_location(json.loads(location))
        else:
            self.debug('Updating location to {0} via http'.format(location))
            DriverManager().update_location(self.driver.id, json.loads(location), self.charge_type) 

        self.write('{}')

class WebSessionDeactivate(LoggableMixin, DriverAuthenticatedWebHandler):

    def __unicode__(self):
        return u'WebSessionDeactivate(D-{id})'.format(id=self.driver.id) if self.is_authenticated else u'WebSessionDeactivate'

    def post(self):
        self.authenticate()

        self.debug('Deactivate user {0}, remove location'.format(self.driver.id))
        DriverManager().deactivate(self.driver.id) 

        self.write('{}')

class WebSessionRequest(LoggableMixin, PassengerAuthenticatedWebHandler):

    def __unicode__(self):
        return u'WebSessionRequest(P-{id})'.format(id=self.passenger.id) if self.is_authenticated else u'WebSessionRequest'

    def post(self):
        self.authenticate()

        source = json.loads(self.get_argument('source'))
        destination = json.loads(self.get_argument('destination'))
        additional_message = json.loads(self.get_argument('additional_message'))

        # Change the states of drivers and passengers accordingly
        WatchManager().unwatch(self.passenger.id)

        # Create a new ride proxy instance
        proxy = RequestProxyManager().create(self.passenger, source, destination, additional_message)
        proxy.request()

        self.write(json.dumps({ 'request_id': proxy._request_id }))


class WebSessionCancel(RideProxyMixin, LoggableMixin, PassengerAuthenticatedWebHandler):

    def __unicode__(self):
        return u'WebSessionCancel(P-{id})'.format(id=self.passenger.id) if self.is_authenticated else u'WebSessionCancel'

    def post(self):
        self.authenticate()

        self.write('{}')

    def post(self, ride_id):
        self.authenticate()

        proxy = self.proxy_by_ride_id(int(ride_id))

        if proxy:
            self.debug('Cancel ride {0}'.format(ride_id))
            proxy.cancel() 
        else:  
            self.debug('No proxy found for {0}, ignore cancel'.format(ride_id))

        self.write('{}')


class WebSessionCancelRide(RideProxyMixin, LoggableMixin, PassengerAuthenticatedWebHandler):

    def __unicode__(self):
        return u'WebSessionCancelRide(P-{id})'.format(id=self.passenger.id) if self.is_authenticated else u'WebSessionCancelRide'

    def post(self, ride_id):
        self.authenticate()

        proxy = self.proxy_by_ride_id(int(ride_id))

        if proxy:
            self.debug('Cancel ride {0}'.format(ride_id))
            proxy.cancel() 
        else:  
            self.debug('No proxy found for {0}, ignore cancel'.format(ride_id))

        self.write('{}')


class WebSessionApprove(RideProxyMixin, LoggableMixin, DriverAuthenticatedWebHandler):

    def __unicode__(self):
        return u'WebSessionApprove(D-{id})'.format(id=self.driver.id) if self.is_authenticated else u'WebSessionApprove'

    def post(self, request_id):
        self.authenticate()

        # try approve
        approved, ride_id = RequestProxyManager().approve(request_id, self.driver.id)        

        if approved:
            self.debug('Approve request {0}'.format(request_id))
            self.write(json.dumps({ 'ride_id': ride_id })) 
        else:
            raise tornado.web.HTTPError(403, 'cannot approve') 
 

class WebSessionReject(RideProxyMixin, LoggableMixin, DriverAuthenticatedWebHandler):

    def __unicode__(self):
        return u'WebSessionReject(D-{id})'.format(id=self.driver.id) if self.is_authenticated else u'WebSessionReject'

    def post(self, request_id):
        self.authenticate()

        # try reject
        RequestProxyManager().reject(request_id, self.driver.id)

        self.debug('Reject request {0}'.format(request_id))

        self.write('{}')

class WebSessionRejectRide(RideProxyMixin, LoggableMixin, DriverAuthenticatedWebHandler):

    def __unicode__(self):
        return u'WebSessionRejectRide(D-{id})'.format(id=self.driver.id) if self.is_authenticated else u'WebSessionRejectRide'

    def post(self, ride_id):
        self.authenticate()

        # try reject
        proxy = self.proxy_by_ride_id(int(ride_id))

        if proxy:
            reason = self.get_argument('reason')
            self.debug('Reject ride {0} with reason {1}'.format(ride_id, reason))
            proxy.reject(reason) 
        else:  
            self.debug('No proxy found for {0}, ignore reject'.format(ride_id))

        self.write('{}')


class WebSessionArrive(RideProxyMixin, LoggableMixin, DriverAuthenticatedWebHandler):

    def __unicode__(self):
        return u'WebSessionArrive(D-{id})'.format(id=self.driver.id) if self.is_authenticated else u'WebSessionArrive'

    def post(self, ride_id):
        self.authenticate()

        proxy = self.proxy_by_ride_id(int(ride_id))

        if proxy:
            self.debug('Arrived ride {0}'.format(ride_id))
            proxy.arrive() 
        else:  
            self.debug('No proxy found for {0}, ignore arrive'.format(ride_id))

        self.write('{}')

class WebSessionBoard(RideProxyMixin, LoggableMixin, DriverAuthenticatedWebHandler):

    def __unicode__(self):
        return u'WebSessionBoard(D-{id})'.format(id=self.driver.id) if self.is_authenticated else u'WebSessionBoard'

    def post(self, ride_id):
        self.authenticate()

        proxy = self.proxy_by_ride_id(int(ride_id))

        if proxy:
            self.debug('Board ride {0}'.format(ride_id))
            proxy.board() 
        else:  
            self.debug('No proxy found for {0}, ignore board'.format(ride_id))

        self.write('{}')

        # remove proxy after 20min

class WebSessionComplete(RideProxyMixin, LoggableMixin, DriverAuthenticatedWebHandler):

    def __unicode__(self):
        return u'WebSessionComplete(D-{id})'.format(id=self.driver.id) if self.is_authenticated else u'WebSessionComplete'

    def post(self, ride_id):
        self.authenticate()

        proxy = self.proxy_by_ride_id(int(ride_id))

        if proxy:
            self.debug('Complete ride {0}'.format(ride_id))
            proxy.complete({}) 
        else:  
            self.debug('No proxy found for {0}, ignore complete'.format(ride_id))

        self.write('{}')

# Server
# ------

class LocationServer(LoggableMixin, SingletonMixin):
    def recover_ride_proxies(self):
        rides = Ride.objects.filter(Q(state=Ride.APPROVED) | Q(state=Ride.ARRIVED)) 

        for ride in rides.all():
            if ride.passenger:
                proxy = RideProxyManager().create(ride.passenger.id, ride.source, ride.destination, ride.additional_message)
                proxy._recover(ride)

    def start(self):
        self.recover_ride_proxies()

        application = tornado.web.Application([
            # websocket
            # ---------
            tornado.web.url(r'/location', Session),
        ])
        application.listen(settings.LOCATION_SERVER_PORT)

        application_web = tornado.web.Application([
            # web 
            # ---

            # driver api
            tornado.web.url(r'/ride/location', WebSessionLocation),
            tornado.web.url(r'/ride/deactivate', WebSessionDeactivate),
            tornado.web.url(r'/ride/approve/([0-9]+)', WebSessionApprove),              # request_id
            tornado.web.url(r'/ride/reject/([0-9]+)', WebSessionReject),                # request_id
            tornado.web.url(r'/ride/reject/ride/([0-9]+)', WebSessionRejectRide),       # ride_id 
            tornado.web.url(r'/ride/arrive/([0-9]+)', WebSessionArrive),                # ride_id
            tornado.web.url(r'/ride/board/([0-9]+)', WebSessionBoard),                  # ride_id
            tornado.web.url(r'/ride/complete/([0-9]+)', WebSessionComplete),            # ride_id

            # passenger api
            tornado.web.url(r'/ride/request', WebSessionRequest),
            tornado.web.url(r'/ride/cancel/([0-9]+)', WebSessionCancel),                # request_id
            tornado.web.url(r'/ride/cancel/ride/([0-9]+)', WebSessionCancelRide),       # ride_id 
        ])
        application_web.listen(settings.LOCATION_WEB_SERVER_PORT)

        self.info('Start serving')

        start()
