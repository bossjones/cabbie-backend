from math import radians, cos, sin, asin, sqrt
from urlparse import urljoin

from django.conf import settings
from rtree.index import Rtree
import requests

from cabbie.utils import json
from cabbie.utils.cache import cached
from cabbie.utils.ds import compact
from cabbie.utils.log import LoggableMixin
from cabbie.utils.meta import SingletonMixin


def haversine(*p):
    """Calculate the great circle distance between two points on the earth
    (specified in decimal degrees)
    """
    if len(p) == 1:
        p1, p2 = p[0]
    else:
        p1, p2 = p

    lon1, lat1 = p1
    lon2, lat2 = p2

    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))

    # 6367 km is the radius of the Earth
    km = 6367 * c
    return km * 1000


# Alias
distance = haversine


class Rtree2D(object):
    """Wrapper of `rtree.Index` for supporting friendly 2d operations.

    Also forces the uniqueness of the `id` parameter, which is different from
    the rtree module's behavior.
    """

    def __init__(self):
        self._index = Rtree()
        self._locations = {}

    @staticmethod
    def to_coords(location):
        return (location[0], location[1], location[0], location[1])

    def keys(self):
        return self._locations.keys()

    def get(self, id, objects=False):
        return self._locations.get(id)

    def set(self, id, location, obj=None):
        # Clean up previous value first if any
        old = self._locations.get(id)
        if old is not None:
            self._index.delete(id, self.to_coords(old))

        self._locations[id] = location
        self._index.insert(id, self.to_coords(location), obj=obj)

    def remove(self, id):
        self._index.delete(id, self.to_coords(self._locations[id]))
        del self._locations[id]

    def nearest(self, location, count=1, objects=False, max_distance=None):
        ids = self._index.nearest(self.to_coords(location), num_results=count,
                                  objects=objects)
        if max_distance is not None:
            ids = [id for id in ids
                   if distance(self._locations[id], location) <= max_distance]
        return ids


class TMapError(Exception)       : pass
class TMapServerError(TMapError) : pass


class TMap(LoggableMixin, SingletonMixin):
    base_url = 'https://apis.skplanetx.com/'
    api_version = '1'
    max_page_size = 200
    cache_timeout = settings.TMAP_CACHE_TIMEOUT

    @classmethod
    def normalize_poi(cls, data):
        return {
            'id': data['id'],
            'name': data['name'],
            'phone': data['telNo'],
            'location': {
                'center': [data['noorLon'], data['noorLat']],
                'front': [data['frontLon'], data['frontLat']],
            },
            'distance': float(data['radius']) * 1000,
            'address': u' '.join(compact([
                data['upperAddrName'],
                data['middleAddrName'],
                data['lowerAddrName'],
                u'-'.join(compact([
                    data['firstNo'],
                    data['secondNo'],
                ])),
                data['detailAddrName'],
            ])),
            # The following fields are optional
            'category': data.get('bizName', ''),
            'full_category': u' > '.join(compact([
                data.get('upperBizName'),
                data.get('middleBizName'),
                data.get('lowerBizName'),
                data.get('detailBizName'),
            ])),
        }
        return tmap_data

    @cached(timeout=cache_timeout)
    def reverse_geocoding(self, location):
        as_json = self._fetch('/tmap/geo/reversegeocoding', {
            'lon': location[0],
            'lat': location[1],
            'coordType': 'WGS84GEO',
            'addressType': 'A02',
        })

        self.info('Successfully fetched for `reverse_geocoding`')

        try:
            result = as_json['addressInfo']
        except KeyError as e:
            self.error('Failed to parse result from TMap: {0}'.format(e))
            raise TMapError(e)
        else:
            return compact(result['fullAddress'])

    def poi_search(self, q, location=None, page=1,
                   count=settings.DEFAULT_PAGE_SIZE):
        all_ = self._poi_search_all(q, location)
        page, count = int(page), int(count)
        start, end = (page - 1) * count, page * count
        return all_[start:end]

    def poi_search_around(self, location, page=1,
                          count=settings.DEFAULT_PAGE_SIZE):
        all_ = self._poi_search_around_all(location)
        page, count = int(page), int(count)
        start, end = (page - 1) * count, page * count
        return all_[start:end]

    @cached(timeout=cache_timeout)
    def _poi_search_all(self, q, location=None):
        params = {
            'page': 1,
            'count': self.max_page_size,
            'searchKeyword': q,
            'searchType': 'all',
            'searchtypCd': 'A',
        }
        if location:
            params.update({
                'searchtypCd': 'R',
                'radius': '0',  # Delegate to server
                'centerLon': location[0],
                'centerLat': location[1],
                'reqCoordType': 'WGS84GEO',
                'resCoordType': 'WGS84GEO',
            })
        as_json = self._fetch('/tmap/pois', params)

        self.info('Successfully fetched for `poi_search`')

        try:
            result = as_json['searchPoiInfo']['pois']['poi']
        except KeyError as e:
            self.error('Failed to parse result from TMap: {0}'.format(e))
            raise TMapError(e)
        else:
            return [self.normalize_poi(data) for data in result]

    @cached(timeout=cache_timeout)
    def _poi_search_around_all(self, location):
        as_json = self._fetch('/tmap/pois/search/around', {
            'page': 1,
            'count': self.max_page_size,
            'centerLon': location[0],
            'centerLat': location[1],
            'reqCoordType': 'WGS84GEO',
            'resCoordType': 'WGS84GEO',
        })

        self.info('Successfully fetched for `poi_search_around`')

        try:
            result = as_json['searchPoiInfo']['pois']['poi']
        except KeyError as e:
            self.error('Failed to parse result from TMap: {0}'.format(e))
            raise TMapError(e)
        else:
            return [self.normalize_poi(data) for data in result]

    def _fetch(self, url, params=None):
        url = urljoin(self.base_url, url)

        params = params or {}
        params['version'] = self.api_version

        headers = {
            'accept': 'application/json',
            'appkey': settings.TMAP_API_KEY,
        }

        self.debug('Fetching {0}'.format(url))

        try:
            r = requests.get(url, params=params, headers=headers)
        except Exception as e:
            self.error('Failed to fetch: {0}'.format(e))
            raise TMapServerError(e)
        else:
            try:
                as_json = json.loads(r.text)
            except Exception as e:
                self.error('Failed to parse json: {0}'.format(e))
                raise TMapError(e)
            else:
                return as_json
