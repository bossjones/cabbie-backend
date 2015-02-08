import traceback
import requests

from django.conf import settings
from tornado import gen
from tornado.websocket import websocket_connect

from cabbie.utils import json
from cabbie.utils.log import LoggableMixin
from cabbie.utils.pubsub import PubsubMixin


class Bot(LoggableMixin, PubsubMixin):
    role = None

    def __init__(self, instance):
        super(Bot, self).__init__()
        self._instance = instance
        self._client = None
        self._stopped = False

    @gen.coroutine
    def connect(self):
        url = 'ws://{host}:{port}/location'.format(
            host=settings.LOCATION_SERVER_HOST,
            port=settings.LOCATION_SERVER_PORT)

        self._client = yield websocket_connect(url)

    @gen.coroutine
    def start(self):
        yield self.connect()

        self.send('auth', {
            'role': self.role,
            'token': self._instance.auth_token.key,
        })

        self.loop()

    @gen.coroutine
    def loop(self):
        while True:
            raw = yield self._client.read_message()
            self.debug(u'Received: {0}'.format(raw))

            if raw is None:
                self.warn('Connection closed')
                self._stopped = True
                break

            try:
                msg = json.loads(raw)
            except Exception as e:
                self.error(u'Failed to parse JSON: {0}'.format(e))
                continue

            type_ = msg['type']
            data = msg.get('data', {})

            method = getattr(self, 'handle_{type_}'.format(type_=type_), None)
            if not method:
                self.warn('Unhandled type: {0}'.format(type_))
                return

            try:
                method(**data)
            except Exception as e:
                self.error(u'Failed to handle: {0}'.format(e))
                traceback.print_exc()

    def send(self, type_, data=None):
        requests.post(self.location_web_url + self.url_mapping[type_]
