import urllib2
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

def post(path, data=None):

    url = urlparse.urljoin('http://{0}:{1}'.format(settings.WEB_SERVER_HOST, settings.WEB_SERVER_PORT), path)

    httpmethod = 'POST'

    headers = {}
    headers["SECRET"] = settings.SECRET_KEY 
    headers["Content-Type"] = 'application/json'

    import sys 
    reload(sys)
    sys.setdefaultencoding('utf-8')

    json_data = json.dumps(data)
    post_data = json_data.encode('utf-8')

    request = urllib2.Request(url, post_data, headers)
    request.get_method = lambda: httpmethod
        
    try:
        response = urllib2.urlopen(request)
    except urllib2.HTTPError, e:
        if e.getcode() == 500:
            response = e 
        else:
            import sys 
            response = "Error executing the request "+ str(sys.exc_info()[1])

    return json.loads(response.read())
