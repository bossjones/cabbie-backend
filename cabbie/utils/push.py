import logging
import threading

from django.conf import settings
from djcelery import celery
from parse_rest.installation import Push


# Thread-specific context
# -----------------------

# As long as we don't use other concurrency scheme than threading
# (e.g. greenlet), just using `threading.Local` should be fine.
_local = threading.local()


class NoPushContext(object):
    def __enter__(self):
        _local.push_enabled = False

    def __exit__(self, type, value, traceback):
        _local.push_enabled = True


# Push Sender
# -----------

logger = logging.getLogger(__name__)


@celery.task
def _send_push_notification(message, channels):
    try:
        Push.message(message, channels=channels)
    except Exception as e:
        logger.error(u'Failed to send push ({0}, {1}): {2}'.format(
            message, channels, e))
    else:
        logger.info(u'Successfully sent push ({0}, {1})'.format(
            message, channels))


def send_push_notification(message, channels, async=True):
    if not getattr(_local, 'push_enabled', True):
        return

    if not settings.DEBUG and async:
        return _send_push_notification.delay(message, channels)
    else:
        return _send_push_notification(message, channels)
