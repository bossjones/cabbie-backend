from django.conf import settings
from django.db.models import Sum

from rest_framework.renderers import JSONRenderer

from cabbie.apps.account.serializers import PassengerSerializer, DriverSerializer
from cabbie.apps.drive.signals import post_ride_complete, post_ride_board
from cabbie.utils.push import send_push_notification
from cabbie.utils import json

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
    # For passenger, send push notification for rating
    passenger = ride.passenger

    # point
    message = {
        'alert': settings.MESSAGE_RIDE_COMPLETE_ALERT,
        'title': settings.MESSAGE_RIDE_COMPLETE_TITLE,
        'push_type': 'ride_completed', 
        'data': {
            'ride_id': ride.id
        }
    }
    send_push_notification(message, ['user_{0}'.format(passenger.id)], False)


post_ride_complete.connect(on_post_ride_complete, dispatch_uid='from_drive')
post_ride_board.connect(on_post_ride_board, dispatch_uid='from_drive')
