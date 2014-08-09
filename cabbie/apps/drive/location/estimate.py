import time
import urllib

from django.conf import settings
from tornado import gen
from tornado.concurrent import Future
from tornado.httpclient import HTTPRequest
from tornado.simple_httpclient import SimpleAsyncHTTPClient

from cabbie.utils import json
from cabbie.utils.geo import haversine
from cabbie.utils.log import LoggableMixin
from cabbie.utils.meta import SingletonMixin
from cabbie.utils.time_ import HOUR


# Exception
# ---------

class TmapException(Exception):
    pass


# Estimator
# ---------

class Estimate(object):
    """Represents estimated distance and time between two locations.

    - distance (in meters)
    - time (in seconds)
    """

    def __init__(self, distance, time):
        self.distance = distance
        self.time = time

    def __unicode__(self):
        return u'Estimate(distance={distance}, time={time})'.format(
            **self.for_json())

    __repr__ = __str__ = __unicode__

    def for_json(self):
        return {
            'distance': self.distance,
            'time': self.time,
        }


class AbstractEstimator(LoggableMixin, SingletonMixin):
    speed = settings.DEFAULT_SPEED

    def estimate(self, source, destination):
        """Should return a future instance."""
        raise NotImplementedError

    def bulk_estimate(self, pairs):
        """Should return a future instance."""
        raise NotImplementedError


class HaversineEstimator(AbstractEstimator):
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
        speed = self.speed * 1000 / HOUR
        time = int(distance / speed)
        return Estimate(distance, time)


class TmapEstimator(AbstractEstimator):
    url = 'https://apis.skplanetx.com/tmap/routes?version=1'
    cache_timeout = settings.TMAP_CACHE_TIMEOUT

    # TODO: Normalized caching (adjusting location to pseudo-location)

    def __init__(self, *args, **kwargs):
        super(TmapEstimator, self).__init__(*args, **kwargs)
        self._caches = {}

    def _get_cache_key(self, source, destination):
        return (tuple(source), tuple(destination))

    def _set_cache(self, source, destination, estimate):
        key = self._get_cache_key(source, destination)
        self._caches[key] = {
            'last': time.time(),
            'estimate': estimate,
        }

    def _get_cache(self, source, destination):
        key = self._get_cache_key(source, destination)
        entry = self._caches.get(key)
        if not entry:
            return None
        if time.time() - entry['last'] >= self.cache_timeout:
            return None
        return entry['estimate']

    @gen.coroutine
    def estimate(self, source, destination, force_refresh=False):
        self.debug('Estimating')

        estimate = self._get_cache(source, destination)
        if estimate:
            raise gen.Return(estimate)

        data = {
            'startX': source[0],
            'startY': source[1],
            'endX': destination[0],
            'endY': destination[1],
            'reqCoordType': 'WGS84GEO',
            'resCoordType': 'WGS84GEO',
            'speed': int(self.speed),
        }
        headers = {
            'accept': 'application/json',
            'appkey': settings.TMAP_API_KEY,
        }
        body = urllib.urlencode(data)
        client = SimpleAsyncHTTPClient()
        request = HTTPRequest(self.url, method='POST', headers=headers,
                              body=body)

        r = yield client.fetch(request)

        data = json.loads(r.body)
        error = data.get('error')
        if error:
            raise TmapException(error)

        prop = data['features'][0]['properties']
        estimate = Estimate(int(prop['totalDistance']), int(prop['totalTime']))

        self._set_cache(source, destination, estimate)

        raise gen.Return(estimate)

    @gen.coroutine
    def bulk_estimate(self, pairs):
        estimates = yield [self.estimate(*pair) for pair in pairs]
        raise gen.Return(estimates)
