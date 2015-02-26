from django.conf import settings
from django.db.models import Sum

from rest_framework.renderers import JSONRenderer

from cabbie.apps.account.serializers import PassengerSerializer, DriverSerializer
from cabbie.apps.drive.signals import post_ride_requested, post_ride_approve, post_ride_reject, post_ride_arrive, post_ride_board, post_ride_complete, post_ride_rated
from cabbie.utils.push import send_push_notification
from cabbie.utils import json

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
    # For passenger, send approve 
    passenger = ride.passenger
    driver = ride.driver

    message = {
        'alert': settings.MESSAGE_RIDE_APPROVE_ALERT,
        'title': settings.MESSAGE_RIDE_APPROVE_TITLE,
        'push_type': 'ride_approved',
        'data': {
            'ride_id': ride.id,
            'driver': {
                'id': driver.id, 
                'name': driver.name,
                'phone': driver.phone,
                'app_version': driver.app_version,
                'license_number': driver.license_number,
                'car_number': driver.car_number,
                'car_model': driver.car_model,
                'company': driver.company,
                'max_capacity': driver.max_capacity,
                'taxi_type': driver.taxi_type,
                'taxi_service': driver.taxi_service,
                'about': driver.about,
                'rated_count': driver.rated_count,
                'ride_count': driver.ride_count,
                'rating': driver.rating,
                'image_urls': driver.image_urls,
            }
        }
    }
    send_push_notification(message, ['user_{0}'.format(passenger.id)], False)


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
post_ride_arrive.connect(on_post_ride_arrive, dispatch_uid='from_drive')
post_ride_board.connect(on_post_ride_board, dispatch_uid='from_drive')
post_ride_complete.connect(on_post_ride_complete, dispatch_uid='from_drive')
