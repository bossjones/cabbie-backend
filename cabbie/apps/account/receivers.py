from django.conf import settings
from rest_framework.authtoken.models import Token

from cabbie.apps.account.models import Passenger, Driver
from cabbie.apps.payment.models import DriverBill, Transaction
from cabbie.apps.drive.signals import post_ride_complete
from cabbie.common.signals import post_create

def on_post_create_user(sender, instance, **kwargs):
    Token.objects.create(user=instance.user_ptr)

def on_post_create_driver_bill(sender, instance, **kwargs):
    driver = instance.driver
    driver.deposit += instance.amount
    driver.save()

def on_post_create_transaction(sender, instance, **kwargs):
    user = instance.user
    user.point += instance.amount
    user.save()

def on_post_ride_complete(sender, ride, **kwargs):
    # For passenger, increase ride count
    passenger = ride.passenger
    passenger.ride_count += 1
    passenger.save()

    # For driver, increase ride count, deduct call fee
    driver = ride.driver
    driver.ride_count += 1
    driver.deposit -= settings.CALL_FEE
    driver.save()


post_create.connect(on_post_create_user, sender=Passenger,
                    dispatch_uid='from_account')
post_create.connect(on_post_create_user, sender=Driver,
                    dispatch_uid='from_account')
post_create.connect(on_post_create_driver_bill, sender=DriverBill,
                    dispatch_uid='from_account')
post_create.connect(on_post_create_transaction, sender=Transaction,
                    dispatch_uid='from_account')
post_ride_complete.connect(on_post_ride_complete,
                    dispatch_uid='from_account')
