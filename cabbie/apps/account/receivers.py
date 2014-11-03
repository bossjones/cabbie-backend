from django.conf import settings
from django.db.models import F
from django.utils import timezone
from rest_framework.authtoken.models import Token

from cabbie.apps.account.models import Passenger, Driver
from cabbie.apps.payment.models import DriverBill, Transaction
from cabbie.apps.drive.signals import post_ride_board
from cabbie.common.signals import post_create


def on_post_create_user(sender, instance, **kwargs):
    Token.objects.create(user=instance.user_ptr)


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


post_create.connect(on_post_create_user, sender=Passenger,
                    dispatch_uid='from_account')
post_create.connect(on_post_create_user, sender=Driver,
                    dispatch_uid='from_account')
post_create.connect(on_post_create_driver_bill, sender=DriverBill,
                    dispatch_uid='from_account')
post_ride_board.connect(on_post_ride_board,
                        dispatch_uid='from_account')
