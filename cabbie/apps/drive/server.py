from collections import defaultdict
import datetime
import time

from django.conf import settings
from rest_framework.authtoken.models import Token
from tornado.concurrent import Future
from tornado.gen import coroutine
import simplejson as json
import tornado.ioloop
import tornado.web
import tornado.websocket

from cabbie.apps.account.models import Driver, Passenger
from cabbie.apps.drive.models import Ride
from cabbie.utils.geo import haversine, Rtree2D
from cabbie.utils.log import LoggableMixin
from cabbie.utils.meta import SingletonMixin
from cabbie.utils.time_ import HOUR, MINUTE


# Module private & Util
# ---------------------

_loop = tornado.ioloop.IOLoop.instance()

def delay(seconds, callback):
    """Friendly shortcut for IOLoop's add_timeout method."""
    _loop.add_timeout(datetime.timedelta(seconds=seconds), callback)


# Estimator
# ---------

class Estimate(object):
    def __init__(self, distance, time):
        self.distance = distance
        self.time = time

    def for_json(self):
        return {
            'distance': self.distance,
            'time': self.time,
        }


class AbstractEstimator(LoggableMixin, SingletonMixin):
    def estimate(self, source, destination):
        """Should return a future instance."""
        raise NotImplementedError

    def bulk_estimate(self, pairs):
        """Should return a future instance."""
        raise NotImplementedError


class HaversineEstimator(AbstractEstimator):
    speed = 40.0 / HOUR  # km per seconds

    def estimate(self, source, destination):
        future = Future()
        future.set_result(self.compute(source, destination))
        return future

    def bulk_estimate(self, pairs):
        future = Future()
        future.set_result([self.compute(source, destination)
                           for source, destination in pairs])
        return future

    def compute(self, p1, p2):
        distance = haversine(p1, p2)
        time = int(distance / self.speed)
        return Estimate(distance, time)


class TmapEstimator(AbstractEstimator):
    def estimate(self, source, destination):
        # FIXME: Implement
        raise NotImplementedError

    def bulk_estimate(self, pairs):
        # FIXME: Implement
        raise NotImplementedError


# Proxy
# -----

class RideProxy(LoggableMixin):
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
        return ObjectManager().get_driver(self._driver_id)

    @property
    def passenger(self):
        return ObjectManager().get_passenger(self._passenger_id)

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
            'passenger': ObjectManager().get_passenger(self._passenger_id),
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


# Managers
# --------

class ObjectManager(LoggableMixin, SingletonMixin):
    """In-memory cache of model instances."""
    expire_interval = 5 * MINUTE

    def __init__(self):
        self._cache = {}

    def get_driver(self, driver_id, **kwargs):
        return self._get_user(Driver, driver_id, **kwargs)

    def get_driver_all(self, driver_ids, **kwargs):
        return self._get_user_all(Driver, driver_ids, **kwargs)

    def get_passenger(self, passenger_id, **kwargs):
        return self._get_user(Passenger, passenger_id, **kwargs)

    def get_passenger_all(self, passenger_ids, **kwargs):
        return self._get_user_all(Passenger, passenger_ids, **kwargs)

    def serialize(self, user):
        serialized = {
            'id': user.id,
            'name': user.name,
            'phone': user.phone,
        }
        if isinstance(user, Passenger):
            serialized.update({
                'ride_count': user.ride_count,
                'rating': 3.5,
            })
        if isinstance(user, Driver):
            serialized.update({
                'ride_count': user.ride_count,
                'licence_number': user.licence_number,
                'rating': 2.5,
            })
        return serialized

    def _get_user(self, model_class, user_id, force_refresh=False,
                  serialize=True):
        now = time.time()
        entry = self._cache.get(user_id)
        if (force_refresh or not entry
                or now - entry['refreshed_at'] >= self.expire_interval):
            entry = {
                'refreshed_at': now,
                'object': model_class.objects.get(pk=user_id),
            }
            self._cache[user_id] = entry
        return self.serialize(entry['object']) if serialize else entry['object']

    def _get_user_all(self, model_class, user_ids, force_refresh=False,
                      serialize=True):
        now = time.time()
        data = {}
        to_refresh = []

        for user_id in user_ids:
            entry = self._cache.get(user_id)
            if (force_refresh or not entry
                    or now - entry['refreshed_at'] >= self.expire_interval):
                to_refresh.append(user_id)
            else:
                data[user_id] = entry['object']

        for user in model_class.objects.filter(id__in=to_refresh):
            data[user.id] = user
            self._cache[user.id] = {'refreshed_at': now, 'object': user}

        if serialize:
            data = dict([(user_id, self.serialize(user))
                         for user_id, user in data.iteritems()])

        return data


class LocationManager(LoggableMixin, SingletonMixin):
    """Dynamic assignment of drivers and passengers using Rtree index."""

    estimator_class = HaversineEstimator
    refresh_interval = 1
    candidate_count = 15

    def __init__(self):
        super(LocationManager, self).__init__()
        self._watches = {}
        self._index = Rtree2D()

        # List of passengers subscribing specific driver's location change
        # TODO: Implement this
        self._subscribers = defaultdict(set)

        self._refresh()

    # Public
    # ------

    def update(self, driver_id, location):
        self._index.set(driver_id, location)

    def remove(self, driver_id):
        try:
            self._index.remove(driver_id)
        except KeyError:
            self.error('Failed to remove {0}'.format(driver_id))

        # FIXME: Re-assign immediately
        # FIXME: Cancel the request or on-going ride process

    def watch(self, passenger_id, location):
        watch = self._watches.get(passenger_id)
        if watch is None:
            watch = {
                'location': location,
                'assignment': None,
            }
            self._watches[passenger_id] = watch
        watch['location'] = location

    def unwatch(self, passenger_id):
        try:
            del self._watches[passenger_id]
        except KeyError:
            self.error('Failed to remove {0}'.format(passenger_id))

    # Private
    # -------

    def _is_same_assignment(self, a1, a2):
        # FIXME: Implement (deep comparison of dict and list objects)
        return False

    def _get_candidates(self, location, count=candidate_count):
        """Return a list of driver candidates."""
        return self._index.nearest(location, count=count)

    def _refresh(self):
        self.debug('Refreshing {0} watches'.format(len(self._watches)))

        zombies = []
        assigned = set()

        drivers = ObjectManager().get_driver_all(self._index.keys())

        def get_assignment(location, driver_id):
            return {
                'driver_id': driver_id,
                'driver': drivers[driver_id],
                'location': self._index.get(driver_id),
                'estimate': HaversineEstimator().compute(
                    location, self._index.get(driver_id)).for_json(),
            }

        for passenger_id, watch in self._watches.iteritems():
            if not SessionManager().is_live(passenger_id):
                zombies.append(passenger_id)
                continue

            location = watch['location']
            prev_assignment = watch['assignment']

            candidates = list(self._get_candidates(location))
            assignment = {}

            # Compute candidates
            assignment['candidates'] = [get_assignment(location, driver_id)
                                        for driver_id in candidates]

            # Compute the best match
            best = None
            for candidate in assignment['candidates']:
                if candidate['driver']['id'] not in assigned:
                    best = candidate
                    assigned.add(candidate['driver']['id'])
                    break
            assignment['best'] = best
            # TODO: Handle the case when all candidates are already assigned

            if not self._is_same_assignment(prev_assignment, assignment):
                SessionManager().get(passenger_id).notify_passenger_assign(
                    assignment)
                watch['assignment'] = assignment

        for passenger_id in zombies:
            del self._watches[passenger_id]

        delay(self.refresh_interval, self._refresh)


class Authenticator(LoggableMixin, SingletonMixin):
    """Authenticates (web)socket connections with token."""

    # TODO: Cache (token, user_id) pair

    def authenticate(self, token, role):
        try:
            user = Token.objects.select_related('user').get(key=token).user
        except Token.DoesNotExist:
            return None
        else:
            # Double check if the user has specified role
            role = user.get_role(role)
            return user.id if role is not None else None


class SessionManager(LoggableMixin, SingletonMixin):
    """Central point to manage all concurrent (web)socket connections."""

    # TODO: Heartbeating periodically to check if connection is live (ping)

    def __init__(self):
        super(SessionManager, self).__init__()
        self._sessions = {}

    def is_live(self, user_id):
        return user_id in self._sessions

    def add(self, user_id, session):
        self._sessions[user_id] = session

    def get(self, user_id):
        return self._sessions.get(user_id)

    def remove(self, user_id):
        try:
            del self._sessions[user_id]
        except KeyError:
            self.error('Failed to remove {0}'.format(user_id))

    def on_add(self, user_id, callback):
        """Register callbacks for connections being newly created."""
        # TODO: Implement
        pass

    def on_remove(self, user_id, callback):
        """Register callbacks for connections being closed."""
        # TODO: Implement
        pass


# Session
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

    def open(self):
        self.debug('Opened')

    def on_close(self):
        if self.authenticated:
            SessionManager().remove(self._user_id)
            if self._role == 'driver':
                LocationManager().remove(self._user_id)
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
            LocationManager().update(self._user_id, location)

    def handle_driver_deactivate(self):
        self.info('Deactivated')

        LocationManager().remove(self._user_id)

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
        LocationManager().watch(self._user_id, location)

    def handle_passenger_request(self, driver_id, location):
        self.info('Requested')

        # Remove driver and passenger from location manager first
        LocationManager().remove(driver_id)
        LocationManager().unwatch(self._user_id)

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

        _loop.start()
