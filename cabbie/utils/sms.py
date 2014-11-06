# encoding: utf-8

import logging
import threading

from coffin.template.loader import render_to_string
from django.conf import settings
from djcelery import celery
from jinja2.exceptions import TemplateError
import requests

from cabbie.utils import json

# Thread-specific context
# -----------------------

# As long as we don't use other concurrency scheme than threading
# (e.g. greenlet), just using `threading.Local` should be fine.
_local = threading.local()


class NoSMSContext(object):
    def __enter__(self):
        _local.sms_enabled = False

    def __exit__(self, type, value, traceback):
        _local.sms_enabled = True


# SMS Sender
# ----------

class SMSException(Exception):
    pass


logger = logging.getLogger(__name__)


@celery.task
def _send_sms_raw(phone, msg, subject=None, from_phone=None, from_name=None):
    logger.info(u'Sending sms to {phone}: {msg}'.format(phone=phone, msg=msg))

    url = 'http://api.openapi.io/ppurio/1/message/sms/kokookko'

    params = {}
    params['send_phone'] = from_phone if from_phone else settings.SMS_FROM
    params['dest_phone'] = phone
    params['msg_body'] = msg

    headers = {
        'x-waple-authorization': settings.SMS_API_KEY
    } 

    try:
        r = requests.post(url, headers=headers, params=params) 
    except Exception as e:
        logger.error(u'Failed to send sms to {phone} with message {msg}: {error}'.format(phone=phone, msg=msg, error=e))
        raise SMSException(e)
    else:
        try:
            as_json = json.loads(r.text)
        except Exception as e:
            logger.error('Failed to send sms to {phone} with json parsing error: {error}'.format(phone=phone, error=e))
        else:
            if as_json['result_code']  != '200':
                logger.error(u'Failed to send sms to {phone} with result code {code}'.format(phone=phone, code=as_json['result_code']))
            
def send_sms_raw(phone, msg, subject=None, from_phone=None, from_name=None,
             async=True):
    if not getattr(_local, 'sms_enabled', True):
        return

    if settings.DEBUG and phone not in settings.ALLOWED_DEBUG_PHONE:
        logger.warn(u'No recipients to send sms due to debug setting')
        return

    if not settings.DEBUG and async:
        return _send_sms_raw.delay(phone, msg, subject, from_phone, from_name)
    else:
        return _send_sms_raw(phone, msg, subject, from_phone, from_name)


default_sms_context = {
    'settings': settings,
}


def send_sms(template, phone, context=None, *args, **kwargs):
    """Template-based shortcut to make it consistent with email interface."""

    sms_context = default_sms_context.copy()
    sms_context.update(context or {})

    try:
        rendered = render_to_string(template, sms_context).strip()
    except TemplateError as e:
        logger.error(u'Failed to render "{0}" sms for {1}: {2}'.format(
            template, phone, e))
        raise SMSException(e)
    else:
        send_sms_raw(phone, rendered, *args, **kwargs)
