from collections import defaultdict
import operator
import time
import operator

from django.conf import settings
from tornado import gen

from cabbie.apps.drive.location.estimate import HaversineEstimator
from cabbie.apps.drive.location.geo import Location
from cabbie.apps.drive.location.model import ModelManager
from cabbie.apps.drive.location.session import SessionManager
from cabbie.utils.geo import distance, Rtree2D
from cabbie.utils.log import LoggableMixin
from cabbie.utils.meta import SingletonMixin
from cabbie.utils.pubsub import PubsubMixin


class DriverManager(LoggableMixin, SingletonMixin, PubsubMixin):
    """Manages the location information of drivers."""

    estimator_class = HaversineEstimator
    estimate_cache_timeout = settings.ESTIMATE_CACHE_TIMEOUT
    estimate_cache_distance = settings.ESTIMATE_CACHE_DISTANCE

    def __init__(self):
        super(DriverManager, self).__init__()
        self._driver_index = Rtree2D()
        self._driver_locations = defaultdict(Location)
        self._driver_charge_types = {}
        self._estimate_cache = {}

        SessionManager().subscribe('driver_closed',
                                   self.on_driver_session_closed)

    @property
    def estimator(self):
        return self.estimator_class()

    # Public
    # ------

    def is_activated(self, driver_id):
        return driver_id in self._driver_locations

    def update_location(self, driver_id, location, charge_type=None):
        is_new = driver_id not in self._driver_locations
        old_charge_type = self._driver_charge_types.get(driver_id)

        self._driver_index.set(driver_id, location)
        self._driver_locations[driver_id].update(location)

        self._driver_charge_types[driver_id] = charge_type

        if is_new:
            self.publish('activated', driver_id, location)
        elif old_charge_type != charge_type:
            self.publish('charge_type_changed', driver_id, location,
                         charge_type)

        self.publish('location_update', driver_id, location)

    def mark_requested(self, driver_id):
        self._driver_index.update(driver_id, 'requested')

    def mark_standby(self, driver_id):
        self._driver_index.update(driver_id, None)

    def deactivate(self, driver_id):
        try:
            self._driver_index.remove(driver_id)
        except KeyError:
            self.error('Failed to remove {0} from index'.format(driver_id))

        last_location = self._driver_locations.get(driver_id)

        try:
            del self._driver_locations[driver_id]
        except KeyError:
            self.error('Failed to remove {0} from locations'.format(driver_id))

        try:
            del self._driver_charge_types[driver_id]
        except KeyError:
            self.error('Failed to remove {0} from charges'.format(driver_id))

        self.publish('deactivated', driver_id, last_location)

    @gen.coroutine
    def get_driver_candidates(self, passenger_id, location, count,
                              max_distance, charge_type=None):
        """Return a list of driver candidates.

        `passenger_id` is only need for caching.
        """
        
        # [(id, state), ... ]
        candidates_with_state = list(
            self.get_nearest_drivers(location, count, max_distance,
                                     charge_type))

        self.debug('candidates: {0}'.format(candidates_with_state))

        # [id, ... ]
        candidates = map(operator.itemgetter(0), candidates_with_state)

        # [state, ... ]
        states = map(operator.itemgetter(1), candidates_with_state)

        # [location, ... ]
        locations = map(self.get_driver_location, candidates)

        estimates = yield self._cached_estimate([(
            (passenger_id, candidates[i]),
            (locations[i], location)
        ) for i in range(len(candidates))])

        drivers = ModelManager().get_driver_all(candidates)

        ret = [{
            'driver': drivers.get(driver_id),
            'location': locations[i],
            'estimate': estimates[i],
            'charge_type': self._driver_charge_types.get(driver_id),
            'state': states[i],
        } for i, driver_id in enumerate(candidates)]

        raise gen.Return(ret)

    @gen.coroutine
    def _cached_estimate(self, pairs):
        estimates = [None] * len(pairs)
        to_compute = []
        now = time.time()

        for i, pair in enumerate(pairs):
            ids, locations = pair
            entry = self._estimate_cache.get(ids)
            if (entry is None
                    or now - entry['last'] >= self.estimate_cache_timeout):
                to_compute.append(i)
                continue

            last_locations = entry['locations']

            # If both source and destination are not that different from the
            # previous estimate, use the cached one instead of re-computing
            distances = map(distance, zip(locations, last_locations))
            if not all([d <= self.estimate_cache_distance for d in distances]):
                to_compute.append(i)
                continue

            self.debug('Estimate cache hit!')
            estimates[i] = entry['estimate']

        computed_estimates = yield self.estimator.bulk_estimate([
            pairs[i][1] for i in to_compute])

        for i, estimate in enumerate(computed_estimates):
            index = to_compute[i]
            estimates[index] = estimate

            ids, locations = pairs[index]
            self._estimate_cache[ids] = {
                'last': now,
                'locations': locations,
                'estimate': estimate,
            }

        raise gen.Return(estimates)

    def get_driver_location(self, driver_id):
        return self._driver_locations.get(driver_id)

    def get_driver_charge_type(self, driver_id):
        return self._driver_charge_types.get(driver_id)

    def get_nearest_drivers(self, location, count=None, max_distance=None,
                            charge_type=None):
        
        # Heuristic
        pseudo_count = count * 3
        ids = self._driver_index.nearest(location, count=pseudo_count,
                                         max_distance=max_distance)

        ids = [
            (id_, state_) for id_, state_ in ids
            if int(self._driver_charge_types[id_]) <= int(charge_type)]

        return ids[:count]

    def on_driver_session_closed(self, user_id, old_session):
        if self.is_activated(user_id):
            self.deactivate(user_id)
