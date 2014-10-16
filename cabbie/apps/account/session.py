# encoding: utf-8

from django.core.cache import cache

from cabbie.utils.log import LoggableMixin
from cabbie.utils.meta import SingletonMixin
from cabbie.utils.sms import send_sms
from cabbie.utils.time_ import MINUTE
from cabbie.utils.verify import issue_verification_code


class InvalidSession(Exception)  : pass
class InvalidCode(Exception)     : pass


class PhoneVerificationSessionManager(LoggableMixin, SingletonMixin):
    timeout = 10 * MINUTE

    def create(self, phone):
        private = issue_verification_code()
        self._set(self._get_cache_key(phone), {
            'private': private,
            'verified': False,
        })

        send_sms('sms/verify_phone.txt', phone, {'code': private})

        return private

    def verify(self, phone, private):
        cache_key = self._get_cache_key(phone)
        entry = self._get(cache_key)
        if not entry:
            raise InvalidSession
        if entry['private'] != private:
            raise InvalidCode

        entry['verified'] = True
        self._set(cache_key, entry)

    def is_verified(self, phone):
        entry = self._get(self._get_cache_key(phone))
        return entry and entry['verified']

    def _get_cache_key(self, phone):
        return 'phone_verification_session.{0}'.format(phone)

    def _set(self, key, data):
        # TODO: Enhance this with persistent storage
        cache.set(key, data, self.timeout)

    def _get(self, key):
        return cache.get(key)

