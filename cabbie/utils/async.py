import Queue
import sys
import threading
import time
import traceback

import simplejson
from tornado.ioloop import PeriodicCallback

from cabbie.utils.log import LoggableMixin
from cabbie.utils.meta import SingletonMixin


class ErrandRunner(LoggableMixin, SingletonMixin, threading.Thread):
    """Process the blocking jobs asynchronously in a separate thread.

    If there is a job that includes a blocking API, just pass the job
    to this manager, then it will run the job in a separate thread and
    invoke the callback function along with the return value of it.
    """

    _stop = object()
    rest_interval = 0.1
    cleanup_interval = 0.5

    def __init__(self):
        super(ErrandRunner, self).__init__()
        self._queue = Queue.Queue()
        self._finished = []
        self._lock = threading.Lock()
        self._cleaner = None
        self._is_active = False

    def do(self, func, callback=lambda x: x, **kwargs):
        """Add a heavy job to queue to get done asynchronously."""

        self._queue.put({
            'func': func,
            'callback': callback,
            'kwargs': kwargs,
        })

    def cleanup(self):
        """Invoke callbacks of the finished jobs."""

        with self._lock:
            while self._finished:
                errand = self._finished.pop(0)

                try:
                    errand['callback'](errand['result'])
                except Exception, e:
                    self.error('An exception while cleaning up async errands '
                               ': %s' % e)
                    traceback.print_exc(file=sys.stderr)

    def run(self):
        """Process the queued jobs in a separate thread.

        This method should be called by a non-main thread since it would entail
        lots of blocking computation.
        """

        while True:
            errand = self._queue.get()

            if errand == self._stop:
                break

            try:
                result = errand['func'](**errand['kwargs'])
            except Exception, e:
                self.error('An exception while running an async job: %s' % e)
                result = None
            finally:
                errand['result'] = result

            with self._lock:
                self._finished.append(errand)

            # Take a break for a while to yield resources to main thread
            time.sleep(self.rest_interval)

    def activate(self):
        if self._is_active:
            self.warn('Already activated')
            return

        self._is_active = True
        self._cleaner = PeriodicCallback(
            self.cleanup, self.cleanup_interval * 1000)
        self._cleaner.start()
        self.start()

    def deactivate(self):
        if not self._is_active:
            self.warn('Not active so cannot be deactivated')
            return

        self._is_active = False
        self._cleaner.stop()
        self._queue.put(self._stop)


class RenderMixin(object):
    def render_json(self, data=None, status=True,
                    content_type='application/json', **header_kwargs):
        response = {
            'status': 'success' if status else 'failure',
            'data': data if data else {},
        }

        self.set_header('Content-Type', content_type)
        for key, value in header_kwargs.iteritems():
            self.set_header(key, value)

        self.write(simplejson.dumps(response))

    def render_error_msg(self, msg, **response_kwargs):
        return self.render_json({'msg': msg}, False)
