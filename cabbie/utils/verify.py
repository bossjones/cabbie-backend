# encoding: utf-8

import logging
import random

from cabbie.utils.sms import send_sms_raw


logger = logging.getLogger(__name__)


def issue_verification_code():
    code = unicode(random.randint(1000, 9999))
    logger.info('Issued new verification code: {0}'.format(code))
    return code


def send_verification_code(phone, code):
    msg = u'[백기사] 가입인증번호 [{code}] 입력시 인증완료됩니다.'.format(code=code)
    send_sms_raw(phone, msg)
