# encoding: utf8

import logging

from cabbie.apps.account.models import Passenger, Driver
from cabbie.apps.notification.models import Notification
from cabbie.apps.notification.signals import notification_created
from cabbie.utils.sms import send_sms_raw


logger = logging.getLogger(__name__)


def on_post_create_notification(sender, notification, **kwargs):
    passengers_qs = (Passengers.objects if notification.is_all_passengers else
                     notification.passengers)
    passengers = passengers_qs.filter(is_active=True)
    for passenger in passengers:
        try:
            send_sms_raw(passenger.phone, notification.body)
        except Exception as e:
            logger.error(u'Failed to send sms to {0}: {1}'.format(
                passenger, e))
        else:
            notification.notified_passenger_count += 1

    drivers_qs = (Driver.objects if notification.is_all_drivers else
                  notification.drivers)
    drivers = drivers_qs.filter(is_active=True, is_accepted=True,
                                is_freezed=False)
    for driver in drivers:
        try:
            send_sms_raw(driver.phone, notification.body)
        except Exception as e:
            logger.error(u'Failed to send sms to {0}: {1}'.format(
                driver, e))
        else:
            notification.notified_driver_count += 1

    notification.save(update_fields=['notified_passenger_count',
                                     'notified_driver_count'])


notification_created.connect(on_post_create_notification,
                             dispatch_uid='from_notification')
