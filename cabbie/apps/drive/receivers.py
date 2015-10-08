from django.conf import settings
from django.db.models import Sum

from rest_framework.renderers import JSONRenderer

from cabbie.apps.drive.signals import post_request_rejected, post_ride_requested, post_ride_approve, post_ride_reject, post_ride_cancel, post_ride_arrive, post_ride_board, post_ride_complete, post_ride_rated
from cabbie.utils.push import send_push_notification
from cabbie.utils.sms import send_sms
from cabbie.utils import json

def on_post_request_rejected(sender, request, **kwargs):
    # send reject push
    passenger = request.passenger

    message = {
        'alert': settings.MESSAGE_RIDE_REJECT_ALERT,
        'title': settings.MESSAGE_RIDE_REJECT_TITLE,
        'push_type': 'request_rejected',
        'data': {
            'request_id': request.id,
        }
    }
    send_push_notification(message, ['user_{0}'.format(passenger.id)], False)


post_request_rejected.connect(on_post_request_rejected, dispatch_uid='from_drive')

def on_post_ride_requested(sender, ride, **kwargs):
    # Send to driver
    driver = ride.driver
    passenger = ride.passenger 

    message = {
        'alert': settings.MESSAGE_RIDE_REQUEST_ALERT,
        'title': settings.MESSAGE_RIDE_REQUEST_TITLE,
        'push_type': 'ride_requested',
        'data': {
            'ride_id': ride.id,
            'passenger': { 
                'id': passenger.id, 
                'name': passenger.name,
                'phone': passenger.phone,
                'email': passenger.email,
            },
            'source': ride.source,
            'destination': ride.destination,
            'additional_message': ride.additional_message,
        }
    }

    send_push_notification(message, ['driver_{0}'.format(driver.id)], False)


def on_post_ride_approve(sender, ride, **kwargs):
    pass


def on_post_ride_reject(sender, ride, **kwargs):
    # For passenger, send reject 
    passenger = ride.passenger

    message = {
        'alert': settings.MESSAGE_RIDE_REJECT_ALERT,
        'title': settings.MESSAGE_RIDE_REJECT_TITLE,
        'push_type': 'ride_rejected',
        'data': {
            'ride_id': ride.id,
            'reason': ride.reason,
        }
    }
    send_push_notification(message, ['user_{0}'.format(passenger.id)], False)

def on_post_ride_cancel(sender, ride, **kwargs):
    # send each information of canceled rides to its QA managers
    if ride.passenger:
        for phone in settings.RIDE_QA_MANAGERS:
            send_sms('sms/canceled_ride.txt', phone, {
                'passenger_phone': ride.passenger.phone,
                'url_for_ride': 'http://admin.bktaxi.com/admin/drive/ride/?id={id}'.format(id=ride.id)
            }) 


def on_post_ride_arrive(sender, ride, **kwargs):
    # For passenger, send arrive 
    passenger = ride.passenger

    message = {
        'alert': settings.MESSAGE_RIDE_ARRIVE_ALERT,
        'title': settings.MESSAGE_RIDE_ARRIVE_TITLE,
        'push_type': 'ride_arrived',
        'data': {
            'ride_id': ride.id
        }
    }
    send_push_notification(message, ['user_{0}'.format(passenger.id)], False)


def on_post_ride_board(sender, ride, **kwargs):
    # For passenger, send  boarded
    passenger = ride.passenger

    # point
    message = {
        'alert': settings.MESSAGE_RIDE_BOARD_ALERT,
        'title': settings.MESSAGE_RIDE_BOARD_TITLE,
        'push_type': 'ride_boarded',
        'data': {
            'ride_id': ride.id
        }
    }
    send_push_notification(message, ['user_{0}'.format(passenger.id)], False)

def on_post_ride_complete(sender, ride, **kwargs):
    pass

post_ride_requested.connect(on_post_ride_requested, dispatch_uid='from_drive')
post_ride_approve.connect(on_post_ride_approve, dispatch_uid='from_drive')
post_ride_reject.connect(on_post_ride_reject, dispatch_uid='from_drive')
post_ride_cancel.connect(on_post_ride_cancel, dispatch_uid='from_drive')
post_ride_arrive.connect(on_post_ride_arrive, dispatch_uid='from_drive')
post_ride_board.connect(on_post_ride_board, dispatch_uid='from_drive')
post_ride_complete.connect(on_post_ride_complete, dispatch_uid='from_drive')
