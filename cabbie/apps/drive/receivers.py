from django.conf import settings

from cabbie.apps.drive.signals import post_ride_complete
from cabbie.utils.push import send_push_notification

def on_post_ride_complete(sender, ride, **kwargs):
    # For passenger, send push notification for rating
    passenger = ride.passenger

    message = { 
        "alert": settings.MESSAGE_RIDE_COMPLETE_ALERT,
        "title": settings.MESSAGE_RIDE_COMPLETE_TITLE
    }
    
    send_push_notification(message, 'Ride', False, # synchronous 
                            where = {"objectId": passenger.parse_installation_object_id}
    )

post_ride_complete.connect(on_post_ride_complete,
                        dispatch_uid='from_drive')
