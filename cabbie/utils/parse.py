import json, httplib, urllib

from django.conf import settings

from cabbie.apps.account.models import Driver
from cabbie.utils.log import LoggableMixin
from cabbie.utils.meta import SingletonMixin

class ParseManager(LoggableMixin, SingletonMixin):
    # helper
    def _get(self, object_name, params=None, headers=None):
        connection = httplib.HTTPSConnection(settings.PARSE_API_URL, settings.PARSE_HTTPS_PORT)
        connection.connect()

        # method
        _method = 'GET'

        # where
        _params = params or {} 
        _where = urllib.urlencode({'where': json.dumps(_params)})

        # header
        _headers = {
            "X-Parse-Application-Id": settings.PARSE_APPLICATION_ID,
            "X-Parse-REST-API-Key": settings.PARSE_REST_API_KEY,
        }
        _headers.update(headers or {})

        # url
        _url = '/1/classes/{0}?{1}'.format(object_name, _where)

        # request
        connection.request(_method, _url, '', _headers)
        result = json.loads(connection.getresponse().read())

        return result

    def _delete(self, object_name, object_id, headers=None):
        connection = httplib.HTTPSConnection(settings.PARSE_API_URL, settings.PARSE_HTTPS_PORT)
        connection.connect()

        # method
        _method = 'DELETE'

        # header
        _headers = {
            "X-Parse-Application-Id": settings.PARSE_APPLICATION_ID,
            "X-Parse-REST-API-Key": settings.PARSE_REST_API_KEY,
        }
        _headers.update(headers or {})

        # url
        _url = '/1/classes/{0}/{1}'.format(object_name, object_id)

        # request
        connection.request(_method, _url, '', _headers)
        result = json.loads(connection.getresponse().read())
        return result

    # remove driver location
    def remove_location(self, driver_id):
        result = self._get(settings.PARSE_OBJECT_DRIVER_LOCATION, params={'driver': driver_id})
        results = result['results']

        if results:
            for result in results:
                object_id = result['objectId']

                self._delete(settings.PARSE_OBJECT_DRIVER_LOCATION, object_id)
