from rest_framework.authtoken.models import Token

from cabbie.apps.account.models import Passenger, Driver
from cabbie.apps.payment.models import DriverBill
from cabbie.common.signals import post_create


def on_post_create_user(sender, instance, **kwargs):
    Token.objects.create(user=instance.user_ptr)

def on_post_create_driver_bill(sender, instance, **kwargs):
    driver = instance.driver
    driver.deposit += instance.amount
    driver.save()

post_create.connect(on_post_create_user, sender=Passenger,
                    dispatch_uid='from_account')
post_create.connect(on_post_create_user, sender=Driver,
                    dispatch_uid='from_account')
post_create.connect(on_post_create_driver_bill, sender=DriverBill,
                    dispatch_uid='from_account')
