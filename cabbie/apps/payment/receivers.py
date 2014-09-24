# encoding: utf8

from django.conf import settings

from cabbie.apps.recommend.models import Recommend
from cabbie.apps.drive.signals import post_ride_complete
from cabbie.apps.payment.models import Transaction
from cabbie.common.signals import post_create


def on_post_create_recommend(sender, instance, **kwargs):
    recommend = instance

    Transaction.objects.create(
        user=recommend.recommender,
        recommend=recommend,
        transaction_type=Transaction.RECOMMEND,
        amount=settings.POINTS_BY_TYPE['recommend'],
    )
    Transaction.objects.create(
        user=recommend.recommendee,
        recommend=recommend,
        transaction_type=Transaction.RECOMMENDED,
        amount=settings.POINTS_BY_TYPE['recommended'],
    )


def on_post_ride_complete(sender, ride, **kwargs):
    note = u''

    if ride.passenger.is_promotion_applicable:
        amount = settings.POINTS_BY_TYPE['mileage_promotion']
        note = u'프로모션 마일리지 적용'
    else:
        amount = settings.POINTS_BY_TYPE['mileage']

    Transactions.objects.create(
        user=ride.passenger,
        ride=ride,
        transaction_type=Transaction.MILEAGE,
        amount=amount,
        note=note,
    )

post_create.connect(on_post_create_recommend, sender=Recommend,
                    dispatch_uid='from_payment')
post_ride_complete.connect(on_post_ride_complete, dispatch_uid='from_payment')
