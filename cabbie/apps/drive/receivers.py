from django.conf import settings
from django.db.models import Sum

from rest_framework.renderers import JSONRenderer

from cabbie.apps.account.serializers import PassengerSerializer, DriverSerializer
from cabbie.apps.drive.signals import post_ride_complete
from cabbie.utils.push import send_push_notification
from cabbie.utils import json

def on_post_ride_complete(sender, ride, **kwargs):
    # For passenger, send push notification for rating
    passenger = ride.passenger

    # point
    from cabbie.apps.payment.models import Transaction
    point = Transaction.objects.filter(ride__id=ride.id).aggregate(point=Sum('amount'))['point']

    from cabbie.apps.drive.serializers import RideSerializer
    ride_serializer = RideSerializer(ride)
    ride = json.loads(json.dumps(ride_serializer.data))

    message = { 
        'alert': settings.MESSAGE_RIDE_COMPLETE_ALERT,
        'title': settings.MESSAGE_RIDE_COMPLETE_TITLE,
        'data': {
            'point': point,
            'ride': ride
        }
    }
   
    send_push_notification(message, ['user_{0}'.format(passenger.id)], False)

post_ride_complete.connect(on_post_ride_complete,
                        dispatch_uid='from_drive')
