import datetime

import tornado.ioloop


_loop = tornado.ioloop.IOLoop.instance()


def delay(seconds, callback):
    """Friendly shortcut for IOLoop's add_timeout method."""
    return _loop.add_timeout(datetime.timedelta(seconds=seconds), callback)

def cancel(timeout):
    _loop.remove_timeout(timeout)


def start():
    _loop.start()
