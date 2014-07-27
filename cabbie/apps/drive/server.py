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
from cabbie.utils.geo import haversine, Rtree2D
from cabbie.utils.log import LoggableMixin
from cabbie.utils.meta import SingletonMixin
from cabbie.utils.time_ import HOUR, MINUTE


_loop = tornado.ioloop.IOLoop.instance()

def delay(seconds, callback):
    _loop.add_timeout(datetime.timedelta(seconds=seconds), callback)


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


class ObjectManager(LoggableMixin, SingletonMixin):
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
        # FIXME: Implement

        serialized = {
            'name': user.name,
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
    estimator_class = HaversineEstimator
    refresh_interval = 1
    candidate_count = 15

    def __init__(self):
        super(LocationManager, self).__init__()
        self._watches = {}
        self._index = Rtree2D()
        # List of passengers subscribing specific driver's location change
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

    def watch(self, passenger_id, location):
        watch = self._watches.get(passenger_id)
        if watch is None:
            watch = {
                'location': location,
                'assignment': None,
            }
            self._watches[passenger_id] = watch
        watch['location'] = location

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

        def get_assignment(location, driver_id):
            return {
                'driver_id': driver_id,
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
                if candidate['driver_id'] not in assigned:
                    best = candidate
                    assigned.add(candidate['driver_id'])
                    break
            assignment['best'] = best
            # TODO: Handle the case when all candidates are already assigned

            if not self._is_same_assignment(prev_assignment, assignment):
                SessionManager().get(passenger_id).notify_assignment(
                    assignment)
                watch['assignment'] = assignment

        for passenger_id in zombies:
            del self._watches[passenger_id]

        delay(self.refresh_interval, self._refresh)


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


class Session(LoggableMixin, tornado.websocket.WebSocketHandler):
    # Websocket handlers
    # ------------------

    def __init__(self, *args, **kwargs):
        super(Session, self).__init__(*args, **kwargs)
        self._user_id = None
        self._role = None

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

        # FIXME
        #def send_request():
            #self.send('driver_requested', {
                #'user_id': 1,
                #'ride_id': 1,
            #})
        #import datetime
        #_loop.add_timeout(datetime.timedelta(seconds=3), send_request)


    # Driver-side
    # -----------

    def handle_driver_update_location(self, location):
        self.debug('Updating location to {0}'.format(location))

        LocationManager().update(self._user_id, location)

    def handle_driver_deactivate(self):
        self.info('Deactivated')

        LocationManager().remove(self._user_id)

    def handle_driver_approve(self, ride_id):
        self.info('Approved')
        pass

    def handle_driver_reject(self, ride_id, reason):
        self.info('Rejected')
        pass

    def handle_driver_arrive(self, ride_id):
        self.info('Arrived')
        pass

    def handle_driver_board(self, ride_id):
        self.info('Boarded')
        pass

    def handle_driver_complete(self, ride_id, rating, comment):
        self.info('Completed')
        pass

    # Passenger-side
    # --------------

    #def handle_passenger_update_location(self, location):
        #self.debug('Updating location to {0}'.format(location))

        #LocationManager().update(self._user_id, location)

    #def handle_passenger_request_cancel(self):
        #self.info('Request cancelled')

    def handle_passenger_watch(self, location):
        self.info('Watched')
        LocationManager().watch(self._user_id, location)

    def handle_passenger_request(self, driver_id, location):
        self.info('Requested')

        # FIXME: Sync data via RideProxy or something
        #ride = RideProxy()

        SessionManager().get(driver_id).send('driver_requested', {
            'passenger_id': self._user_id,
            'passenger': ObjectManager().get_passenger(self._user_id),
            'location': location,
        })

    def handle_passenger_cancel(self, ride_id):
        self.info('Cancelled')

    def notify_assignment(self, assignment):
        self.debug('Notifying new assignment: {0}'.format(assignment))
        self.send('passenger_assigned', {
            'assignment': assignment,
        })


class LocationServer(LoggableMixin, SingletonMixin):
    def start(self):
        application = tornado.web.Application([
            (r'/location', Session),
        ])
        application.listen(settings.LOCATION_SERVER_PORT)

        self.info('Start serving')

        _loop.start()
