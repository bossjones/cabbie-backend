import time

from django.conf import settings

from cabbie.apps.account.models import Driver, Passenger
from cabbie.utils.log import LoggableMixin
from cabbie.utils.meta import SingletonMixin


class ModelManager(LoggableMixin, SingletonMixin):
    """In-memory cache of model instances."""
    cache_timeout = settings.OBJECT_CACHE_TIMEOUT

    def __init__(self):
        super(ModelManager, self).__init__()
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
            'app_version': user.app_version,
        }
        if isinstance(user, Passenger):
            serialized.update({
            })
        if isinstance(user, Driver):
            serialized.update({
                'is_freezed': user.is_freezed,
                'license_number': user.license_number,
                'car_number': user.car_number,
                'car_model': user.car_model,
                'company': user.company,
                'max_capacity': user.max_capacity,
                'taxi_type': user.taxi_type,
                'taxi_service': user.taxi_service,
                'about': user.about,
                'rated_count': user.rated_count,
                'ride_count': user.ride_count,
                'rating': user.rating,
                'image_urls': user.get_image_urls(),
            })
        return serialized

    def _get_user(self, model_class, user_id, force_refresh=False,
                  serialize=True):
        now = time.time()
        entry = self._cache.get(user_id)
        if (force_refresh or not entry
                or now - entry['refreshed_at'] >= self.cache_timeout):
            entry = {
                'refreshed_at': now,
                'object': model_class.objects.get(pk=user_id),
            }
            self._cache[user_id] = entry
        return (self.serialize(entry['object'])
                if serialize else entry['object'])

    def _get_user_all(self, model_class, user_ids, force_refresh=False,
                      serialize=True):
        now = time.time()
        data = {}
        to_refresh = []

        for user_id in user_ids:
            entry = self._cache.get(user_id)
            if (force_refresh or not entry
                    or now - entry['refreshed_at'] >= self.cache_timeout):
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

    def _get_ride_cache_key(self, ride_id):
        return 'ride_{id}'.format(id=ride_id)

    def get_ride(self, ride_id, **kwargs):
        return self._get_ride(ride_id, **kwargs)

    def _get_ride(self, ride_id, force_refresh=False, serialize=True):
        now = time.time()
        cache_key = self._get_ride_cache_key(ride_id)

        entry = self._cache.get(cache_key)
        if (force_refresh or not entry
                or now - entry['refreshed_at'] >= self.cache_timeout):
            entry = {
                'refreshed_at': now,
                'object': Ride.objects.get(pk=ride_id),
            }
            self._cache[cache_key] = entry
        return (self.serialize(entry['object'])
                if serialize else entry['object'])


