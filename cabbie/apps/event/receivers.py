# -*- coding: utf-8 -*-
import datetime, httplib, json
import xml.etree.ElementTree as ET
import requests
import base64

from django.conf import settings
from django.db.models import F
from django.utils import timezone
from tornado import gen
from rest_framework.authtoken.models import Token

from cabbie.common.signals import post_create, post_delete
from cabbie.apps.event.models import CuEventPassengers

from cabbie.utils.seed import SEED

def on_post_create_cu_event_passenger(sender, instance, **kwargs):
    if not instance.passenger:
        return

    # url
    url = 'http://{host_port}'.format(host_port=settings.CU_GIFT_SERVER)
    path = 'cu/linkPublishLimit.do'

    # header
    headers = {}

    # data 
    data = {}
    data['COM_KEY'] = '186'
    data['SEL_PRD_NO'] = '2015111001'                   # TODO: changed later 
    data['TR_TEL'] = encode(instance.passenger.phone)   # recepient number 
    #data['MMS_MSG'] = u'백기사 가입에 감사드리며 보내드리는 프로모션 상품입니다.'   # TODO: change later
    data['ORD_NO'] = instance.id                        # any unique number within bktaxi
    data['BUY_PRC'] = '1520'                              # 5% discount from 1600 
    data['ORD_TEL'] = encode(settings.SMS_FROM) 
    data['TRAN_GB'] = '0'   # '0': issue, '1': cancel, '2': PIN issue, '3': PIN cancel
    #data['ISSUE_APP_NO'] =  
    #data['ISSUE_APP_DAY'] = 
    #data['CHARSET'] = 
    #data['CANCEL_GB'] = 
    data['USE_ACC'] = 'N' 

    # added
    data['PIN_YN'] = '0' 
    data['SMS_MSG'] = u'프리미엄 콜택시 앱 백기사 가입 상품\n(첫 탑승 시 2만 포인트 적립 이벤트 진행 중)'   # content 
    data['ORD_QTY'] = '1'

    response = requests.post(url + '/' + path, data=data)
    print response.text

    success, response_code, pin_no, response_message, auth_id, auth_date = interpret(response.text)

    if success:
        instance.make_gift_sent()

    # for DEBUG purpose
    instance.api_response_code = response_code
    instance.pin_no = pin_no
    instance.res_msg = response_message
    instance.auth_id = auth_id
    instance.auth_date = auth_date
    instance.save(update_fields=['api_response_code', 'pin_no', 'res_msg', 'auth_id', 'auth_date'])
    
            

def interpret(response):
    root = ET.fromstring(response)
    success = False
    response_code = None 
    pin_no = None
    response_message = None
    auth_id = None
    auth_date = None
    
    # RES_CODE 
    for response in root.iter('RES_CODE'):
        response_code = response.text
        break

    # PIN_NO
    for pin in root.iter('PIN_NO'):
        pin_no = pin.text
        break

    # RES_MSG
    for response in root.iter('RES_MSG'):
        response_message = response.text
        break

    # AUTH_ID
    for auth_id in root.iter('AUTH_ID'):
        auth_id = auth_id.text
        break

    # AUTH_DATE
    for date in root.iter('DATE'):
        auth_date = date.text
        break

    if '00' == response_code:
        success = True

    print '[CU] response_code: {0}, pin_no: {1}'.format(response_code, pin_no)

    return success, response_code, pin_no, response_message, auth_id, auth_date

def encode(data):
    # SEED 
    s = SEED()

    # ensure data length 16byte
    padding = 16 - len(data)
    data += chr(padding) * padding

    # key
    SEED_KEY = '-f_LGX14Lx9rnibU' 
    k = s.SeedRoundKey(SEED_KEY)

    encrypted = s.SeedEncrypt(data, k)
    
    # base64 encoding
    encrypted = base64.encodestring(encrypted) 

    return encrypted[:-1]   # trim rightmost \n


post_create.connect(on_post_create_cu_event_passenger, sender=CuEventPassengers,
                    dispatch_uid='from_event')
