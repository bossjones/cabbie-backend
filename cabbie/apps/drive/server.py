from django.conf import settings
import tornado.ioloop
import tornado.web

from cabbie.utils.async import AbstractHandler
from cabbie.utils.log import LoggableMixin
from cabbie.utils.meta import SingletonMixin


class LocationHandler(AbstractHandler):
    def get(self):
        self.render_json({ 'foo': 'boo' })


class LocationServer(LoggableMixin, SingletonMixin):
    def start(self):
        application = tornado.web.Application([
            (r'/_', LocationHandler),
        ])
        application.listen(settings.LOCATION_SERVER_PORT)

        self.info('Start serving')

        tornado.ioloop.IOLoop.instance().start()
