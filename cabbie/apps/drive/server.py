from django.conf import settings
import tornado.ioloop
import tornado.web
import tornado.websocket

from cabbie.utils.log import LoggableMixin
from cabbie.utils.meta import SingletonMixin


class LocationHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        self.debug('Opened')

    def on_close(self):
        self.debug('Closed')

    def on_message(self, message):
        self.debug('Received: {0}'.format(message))


class LocationServer(LoggableMixin, SingletonMixin):
    def start(self):
        application = tornado.web.Application([
            (r'/_', LocationHandler),
        ])
        application.listen(settings.LOCATION_SERVER_PORT)

        self.info('Start serving')

        tornado.ioloop.IOLoop.instance().start()
