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
        }
        if isinstance(user, Passenger):
            serialized.update({
                'ride_count': user.ride_count,
                'rating': 3.5,
            })
        if isinstance(user, Driver):
            serialized.update({
                'ride_count': user.ride_count,
                'license_number': user.license_number,
                'company': user.company,
                'car_number': user.car_number,
                'rating': 2.5,
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


