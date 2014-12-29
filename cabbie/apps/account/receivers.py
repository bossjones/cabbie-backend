# -*- coding: utf-8 -*-
from django.conf import settings
from django.db.models import F
from django.utils import timezone
from rest_framework.authtoken.models import Token

from cabbie.apps.account.models import Passenger, Driver, DriverReservation
from cabbie.apps.payment.models import DriverBill, Transaction
from cabbie.apps.drive.signals import post_ride_board
from cabbie.common.signals import post_create
from cabbie.utils.email import send_email


def on_post_create_driver(sender, instance, **kwargs):
    Token.objects.create(user=instance.user_ptr)

    # update driver reservation
    try:
        driver_reservation = DriverReservation.objects.get(phone=instance.phone)
    except DriverReservation.DoesNotExist:
        pass
    else:
        driver_reservation.join()

def on_post_create_passenger(sender, instance, **kwargs):
    Token.objects.create(user=instance.user_ptr)

    # send email to passenger
    if sender is Passenger:
        send_email('mail/passenger_signup.txt', instance.email, {'subject': '{name}님 환영합니다'.format(name=instance.name), 'message': '백기사에 가입해 주셔서 감사합니다.'})




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
post_create.connect(on_post_create_driver_bill, sender=DriverBill,
                    dispatch_uid='from_account')
post_ride_board.connect(on_post_ride_board,
                        dispatch_uid='from_account')
