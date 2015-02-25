# scripts/mock_driver.py

import requests

from rest_framework.authtoken.models import Token
from django.conf import settings

from cabbie.apps.account.models import Driver
from cabbie.utils import json

url_mapping = {
    'request': '/ride/request',
    'approve': '/ride/approve/{0}',
    'reject': '/ride/reject/{0}',
    'reject_ride': '/ride/reject/ride/{0}',
    'cancel': '/ride/cancel/{0}',
    'cancel_ride': '/ride/cancel/ride/{0}',
}

def get_token(user_id):
    try:
        token = Token.objects.get(user_id=user_id)
    except Token.DoesNotExist, e:
        print 'cannot find user {0}\'s token'.format(user_id)
        return None
    else:
        return token
    
def run(*args):
    args = args[0].split(',')
    command_ = args[0]

    host = 'http://{host}:{port}'.format(host=settings.LOCATION_SERVER_HOST, 
                                        port=settings.LOCATION_WEB_SERVER_PORT) 
    payload = {}

    if command_ == 'request':
        if len(args) != 2:
            print 'argument request,{passenger_id}'
            return 
        else:
            user_id_ = args[1]

            # url
            url = '{host}{url}'.format(host=host, url=url_mapping[command_])

            # header
            token = get_token(user_id_)
            if token is None:
                return
            headers = { 'Authorization': 'Token {0}'.format(token) }

            # data
            payload['source'] = json.dumps({'location':[126.979626, 37.570729]}) 
            payload['destination'] = json.dumps({ 'location':[126.979626, 37.570729]}) 
            payload['additional_message'] = json.dumps({})    


    elif command_ == 'approve':
        if len(args) != 3:
            print 'argument approve,{request_id},{driver_id}'
            return 
        else:
            request_id_ = args[1]
            user_id_ = args[2]
                
            # url
            url = '{host}{url}'.format(host=host, url=url_mapping[command_])
            url = url.format(request_id_)

            # header
            token = get_token(user_id_)
            if token is None:
                return
            headers = { 'Authorization': 'Token {0}'.format(token) }


    elif command_ == 'reject':
        if len(args) != 3:
            print 'argument reject,{request_id},{driver_id}'
            return
        else:
            request_id_ = args[1]
            user_id_ = args[2]

            # url
            url = '{host}{url}'.format(host=host, url=url_mapping[command_])
            url = url.format(request_id_)

            # header
            token = get_token(user_id_)
            if token is None:
                return
            headers = { 'Authorization': 'Token {0}'.format(token) }


    elif command_ == 'reject_ride':
        if len(args) != 3:
            print 'argument reject_ride,{ride_id},{driver_id}'
            return
        else:
            ride_id_ = args[1]
            user_id_ = args[2]

            # url
            url = '{host}{url}'.format(host=host, url=url_mapping[command_])
            url = url.format(ride_id_)

            # header
            token = get_token(user_id_)
            if token is None:
                return
            headers = { 'Authorization': 'Token {0}'.format(token) }

            # data
            payload['reason'] = 'after'

    elif command_ == 'cancel':
        if len(args) != 3:
            print 'argument cancel,{request_id},{passenger_id}'
            return 
        else:
            request_id_ = args[1]
            user_id_ = args[2]
                
            # url
            url = '{host}{url}'.format(host=host, url=url_mapping[command_])
            url = url.format(request_id_)

            # header
            token = get_token(user_id_)
            if token is None:
                return
            headers = { 'Authorization': 'Token {0}'.format(token) }


    elif command_ == 'cancel_ride':
        if len(args) != 3:
            print 'argument cancel_ride,{ride_id},{passenger_id}'
            return
        else:
            ride_id_ = args[1]
            user_id_ = args[2]

            # url
            url = '{host}{url}'.format(host=host, url=url_mapping[command_])
            url = url.format(ride_id_)

            # header
            token = get_token(user_id_)
            if token is None:
                return
            headers = { 'Authorization': 'Token {0}'.format(token) }



    ret = requests.post(url, data=payload, headers=headers) 
    print ret.text
