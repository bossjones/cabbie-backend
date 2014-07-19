from django.conf import settings
import simplejson as json
import tornado.ioloop
import tornado.web
import tornado.websocket

from cabbie.utils.log import LoggableMixin
from cabbie.utils.meta import SingletonMixin


class LocationHandler(LoggableMixin, tornado.websocket.WebSocketHandler):
    def open(self):
        self.debug('Opened')

    def on_close(self):
        self.debug('Closed')

    def on_message(self, message):
        as_json = json.loads(message);
        self.debug('Received: {0}'.format(as_json))


class LocationServer(LoggableMixin, SingletonMixin):
    def start(self):
        application = tornado.web.Application([
            (r'/location', LocationHandler),
        ])
        application.listen(settings.LOCATION_SERVER_PORT)

        self.info('Start serving')

        tornado.ioloop.IOLoop.instance().start()
