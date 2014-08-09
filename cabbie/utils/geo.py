from math import radians, cos, sin, asin, sqrt

from rtree.index import Rtree


def haversine(*p):
    if len(p) == 1:
        p1, p2 = p[0]
    else:
        p1, p2 = p

    """Calculate the great circle distance between two points on the earth
    (specified in decimal degrees)
    """
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
            ids = [id for id in ids if distance(self._locations[id], location)
                                       <= max_distance]
        return ids
