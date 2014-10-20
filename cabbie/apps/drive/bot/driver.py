from django.conf import settings
from tornado import gen
from tornado.websocket import websocket_connect

from cabbie.utils import json
from cabbie.utils.log import LoggableMixin


class Bot(LoggableMixin):
    role = None

    def __init__(self, instance):
        super(Bot, self).__init__()
        self._instance = instance
        self._client = None

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

    def send(self, type_, data=None):
        self._client.write_message(json.dumps({
            'type': type_,
            'data': data or {},
        }))


class PassengerBot(Bot):
    role = 'passenger'


class DriverBot(Bot):
    role = 'driver'
