import random
import time

from django.conf import settings


class DelayMiddleware(object):
    enable = True
    delay = 500
    randomize = True

    def process_request(self, request):
        if not settings.DEBUG or not self.enable:
            return

        time.sleep(max(0, (random.gauss(self.delay, self.delay / 2.0)
                           if self.randomize else self.delay) / 1000.0))
