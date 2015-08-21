# encoding: utf8

import logging

from cabbie.apps.account.models import Passenger, Driver
from cabbie.apps.notification.models import Notification
from cabbie.apps.notification.signals import notification_created
from cabbie.utils.sms import send_sms_raw


logger = logging.getLogger(__name__)


def on_post_create_notification(sender, notification, **kwargs):
    # for passengers 
    # -----------
    passengers_qs = (Passenger.objects if notification.is_all_passengers else
                     notification.passengers)
    passengers = passengers_qs.filter(is_active=True, is_sms_agreed=True)
    for passenger in passengers:
        try:
            send_sms_raw(passenger.phone, notification.body)
        except Exception as e:
            logger.error(u'Failed to send sms to {0}: {1}'.format(
                passenger, e))
        else:
            notification.notified_passenger_count += 1

    # for drivers
    # -----------
    drivers_qs = None

    if notification.drivers:
        # unconditional filter
        drivers_qs = notification.drivers.filter(is_active=True, is_accepted=True, is_sms_agreed=True) 
    else:
        # unconditional filter
        drivers_qs = Driver.objects.filter(is_active=True, is_accepted=True, is_sms_agreed=True)

        # conditional filter
        if not notification.is_all_drivers:
            filters = {}
            filters['is_freezed'] = notification.is_freezed or False

            if notification.education:
                filters['education'] = notification.education

            if notification.province:
                filters['province'] = notification.province

            if notification.region:
                filters['region'] = notification.region

            drivers_qs = drivers_qs.filter(**filters) 

    drivers = drivers_qs

    # send sms
    for driver in drivers:
        try:
            if not notification.is_test:
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
