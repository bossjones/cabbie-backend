import logging


logger = logging.getLogger(__name__)


def send_sms(phone, msg):
    logger.info(u'Sending sms to {phone}: {msg}'.format(phone=phone, msg=msg))
    # FIXME: Implement
