from collections import defaultdict

from tornado import gen
from django.conf import settings

from cabbie.apps.drive.location.estimate import TmapEstimator
from cabbie.apps.drive.location.model import ModelManager
from cabbie.apps.drive.location.session import SessionManager
from cabbie.utils.geo import distance, Rtree2D
from cabbie.utils.log import LoggableMixin
from cabbie.utils.meta import SingletonMixin
from cabbie.utils.pubsub import PubsubMixin


class Location(list):
    """Represents longitude and latitude pair. Should be updated regularly."""

    def __init__(self, *args, **kwargs):
        super(Location, self).__init__(*args, **kwargs)
        self._ensure_size()

    def __unicode__(self):
        return u'Location({location})'.format(location=list(self))

    __repr__ = __str__ = __unicode__

    def update(self, location):
        assert len(location) == 2, 'Wrong size'
        for i, coord in enumerate(location):
            self[i] = coord

    def _ensure_size(self):
        while len(self) < 2:
            self.append(0)


class LocationManager(LoggableMixin, SingletonMixin, PubsubMixin):
    """Manages the location information of drivers."""

    estimator_class = TmapEstimator
    candidate_count = settings.CANDIDATE_COUNT
    max_distance = settings.MAX_DISTANCE

    def __init__(self):
        super(LocationManager, self).__init__()
        self._driver_index = Rtree2D()
        self._driver_locations = defaultdict(Location)

        SessionManager().subscribe('driver_closed',
                                   self.on_driver_session_closed)

    @property
    def estimator(self):
        return self.estimator_class()

    # Public
    # ------

    def update_location(self, driver_id, location):
        is_new = driver_id in self._driver_locations

        self._driver_index.set(driver_id, location)
        self._driver_locations[driver_id].update(location)

        if is_new:
            self.publish('activated', driver_id, location)

        self.publish('location_update', driver_id, location)

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

        self.publish('deactivated', driver_id, last_location)

    @gen.coroutine
    def get_driver_candidates(self, location, count=candidate_count,
                              max_distance=max_distance):
        """Return a list of driver candidates."""

        candidates = list(
            self.get_nearest_driver_ids(location, count, max_distance))
        locations = map(self.get_driver_location, candidates)
        estimates = yield self.estimator.bulk_estimate([
            (source, location) for source in locations])
        drivers = ModelManager().get_driver_all(candidates)
        raise gen.Return([{
            'driver': drivers[driver_id],
            'location': locations[i],
            'estimate': estimates[i],
        } for i, driver_id in enumerate(candidates)])

    def get_driver_location(self, driver_id):
        return self._driver_locations.get(driver_id)

    def get_nearest_driver_ids(self, location, count=None, max_distance=None):
        return self._driver_index.nearest(location, count=count,
                                          max_distance=max_distance)

    def on_driver_session_closed(self, user_id, old_session):
        self.deactivate(user_id)
