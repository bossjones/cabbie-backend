import urllib
import urlparse

from django.conf import settings
from tornado import gen
from tornado.httpclient import HTTPRequest
from tornado.simple_httpclient import SimpleAsyncHTTPClient

from cabbie.utils import json


@gen.coroutine
def fetch(path, data=None):
    url = urlparse.urljoin('http://{0}:{1}'.format(settings.WEB_SERVER_HOST, settings.WEB_SERVER_PORT), path)

    body = json.dumps(data or {})
    headers = {'SECRET': settings.SECRET_KEY}

    client = SimpleAsyncHTTPClient()
    request = HTTPRequest(url, method='POST', headers=headers,
                          body=body)

    r = yield client.fetch(request)
    raise gen.Return(json.loads(r.body))
