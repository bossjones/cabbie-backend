# -*- coding: utf-8 -*-
import datetime

from django.conf import settings
from django.db.models import F
from django.utils import timezone
from rest_framework.authtoken.models import Token

from cabbie.apps.account import messages
from cabbie.apps.account.models import Passenger, Driver, DriverReservation
from cabbie.apps.payment.models import DriverBill, Transaction
from cabbie.apps.drive.signals import post_ride_board
from cabbie.common.signals import post_create
from cabbie.utils.email import send_email
from cabbie.utils.sms import send_sms


def on_post_create_driver(sender, instance, **kwargs):
    Token.objects.create(user=instance.user_ptr)

    # update driver reservation
    try:
        driver_reservation = DriverReservation.objects.get(phone=instance.phone)
    except DriverReservation.DoesNotExist:
        pass
    else:
        driver_reservation.join()

def on_post_create_driver_reservation(sender, instance, **kwargs):
    
    # send to driver account admin
    for phone in settings.DRIVER_ACCOUNT_MANAGER:
        send_sms('sms/driver_reservation.txt', phone, {
            'name': instance.name,
            'phone': instance.phone,
            'car_model': instance.car_model,
        })

def on_post_create_passenger(sender, instance, **kwargs):
    Token.objects.create(user=instance.user_ptr)

    # send email to passenger
    if sender is Passenger and instance.is_email_agreed:
        send_email('mail/signup_completed.html', instance.email, {
            # common
            'cdn_url': settings.EMAIL_CDN_DOMAIN_NAME,
            'email_font': settings.EMAIL_DEFAULT_FONT,
            'bktaxi_web_url': settings.BKTAXI_WEB_URL,
            'bktaxi_facebook_url': settings.BKTAXI_FACEBOOK_URL,
            'bktaxi_instagram_url': settings.BKTAXI_INSTAGRAM_URL,
            'bktaxi_naver_blog_url': settings.BKTAXI_NAVER_BLOG_URL,

            'subject': messages.ACCOUNT_EMAIL_SUBJECT_SIGNUP_COMPLETED,
            'user': instance,
        })

    # signup point
    due_date = datetime.datetime.strptime(settings.BKTAXI_PASSENGER_SIGNUP_POINT_DUE_DATE, "%Y-%m-%d").date()
    due_date = due_date + datetime.timedelta(days=1)

    today = datetime.date.today()

    if today < due_date: 
        transaction_type = Transaction.SIGNUP_POINT
        amount = settings.POINTS_BY_TYPE.get(transaction_type)
        if amount:
            Transaction.objects.create(
                user=instance,
                transaction_type=transaction_type,
                amount=amount,
                state=Transaction.DONE,
                note=Transaction.get_transaction_type_text(transaction_type)
            )

    # send sms for recommend event
    event_ends_at = datetime.datetime.strptime(settings.BKTAXI_PASSENGER_RECOMMEND_EVENT_SMS_SEND_ENDS_AT, "%Y-%m-%d").date()
    event_ends_at = event_ends_at + datetime.timedelta(days=1)

    today = datetime.date.today()

    if today < event_ends_at:
        send_sms('sms/passenger_recommend_event.txt', instance.phone, {})



def on_post_create_driver_bill(sender, instance, **kwargs):
    driver = instance.driver
    driver.deposit += instance.amount
    driver.save(update_fields=['deposit'])


def on_post_ride_board(sender, ride, **kwargs):
    # For passenger, increase ride count
    passenger = ride.passenger
    passenger.board_count = F('board_count') + 1
    passenger.current_month_board_count = F('current_month_board_count') + 1
    passenger.last_active_at = timezone.now()
    passenger.save(update_fields=['board_count', 'last_active_at'])

    # For driver, increase ride count, deduct call fee
    driver = ride.driver
    driver.board_count = F('board_count') + 1
    driver.current_month_board_count = F('current_month_board_count') + 1
    driver.last_active_at = timezone.now()
    driver.deposit = F('deposit') - settings.CALL_FEE
    driver.save(update_fields=['board_count', 'last_active_at', 'deposit'])


post_create.connect(on_post_create_passenger, sender=Passenger,
                    dispatch_uid='from_account')
post_create.connect(on_post_create_driver, sender=Driver,
                    dispatch_uid='from_account')
post_create.connect(on_post_create_driver_reservation, sender=DriverReservation,
                    dispatch_uid='from_account')
post_create.connect(on_post_create_driver_bill, sender=DriverBill,
                    dispatch_uid='from_account')
post_ride_board.connect(on_post_ride_board,
                        dispatch_uid='from_account')
