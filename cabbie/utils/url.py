import urllib
import urlparse

from django.conf import settings


def get_url_path(url):
    return urlparse.urlparse(url).path

def get_url_host(url):
    return urlparse.urlparse(url).netloc

def strip_trailing_slashes(url):
    return url.rstrip('/')

def add_url_params(url, data):
    parsed = list(urlparse.urlparse(url))
    params = dict(urlparse.parse_qsl(parsed[4]))
    params.update(data)
    parsed[4] = urllib.urlencode(params)
    return urlparse.urlunparse(parsed)

def add_url_param(url, key, value):
    return add_url_params(url, { key: value })

def remove_url_params(url, *keys):
    parsed = list(urlparse.urlparse(url))
    params = dict(urlparse.parse_qsl(parsed[4]))
    for key in keys:
        try:
            del params[key]
        except Exception:
            pass
    parsed[4] = urllib.urlencode(params)
    return urlparse.urlunparse(parsed)

def get_url_param(url, key):
    parsed = list(urlparse.urlparse(url))
    params = dict(urlparse.parse_qsl(parsed[4]))
    return urllib.unquote(params.get(key, ''))

def absolutify(url, host=settings.HOST, scheme='http'):
    return urlparse.urljoin('{scheme}://{host}'.format(
        scheme=scheme, host=host), url)

def ensure_protocol(url, default='http'):
    return urlparse.urljoin('{0}://'.format(default), url)
