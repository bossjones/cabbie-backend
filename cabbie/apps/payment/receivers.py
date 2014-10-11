# encoding: utf8

from django.conf import settings

from cabbie.apps.recommend.models import Recommend
from cabbie.apps.drive.signals import post_ride_complete
from cabbie.apps.payment.models import Transaction
from cabbie.common.signals import post_create


def on_post_create_recommend(sender, instance, **kwargs):
    recommend = instance

    amount = settings.POINTS_BY_TYPE.get(
        'recommend_{0}'.format(recommend.recommend_type))
    if amount:
        Transaction.objects.create(
            user=recommend.recommender,
            recommend=recommend,
            transaction_type=Transaction.RECOMMEND,
            amount=amount,
        )

    amount = settings.POINTS_BY_TYPE.get(
        'recommended_{0}'.format(recommend.recommend_type))
    if amount:
        Transaction.objects.create(
            user=recommend.recommendee,
            recommend=recommend,
            transaction_type=Transaction.RECOMMENDED,
            amount=amount,
        )

def on_post_ride_complete(sender, ride, **kwargs):
    # For passenger
    passenger = ride.passenger
    note = u''

    # Basic mileage
    if passenger.is_promotion_applicable:
        amount = settings.POINTS_BY_TYPE['mileage_promotion']
        note = u'프로모션 마일리지 적용'
    else:
        amount = settings.POINTS_BY_TYPE['mileage']

    Transaction.objects.create(
        user=passenger,
        ride=ride,
        transaction_type=Transaction.MILEAGE,
        amount=amount,
        note=note,
    )

    # Bonus mileage
    qs = passenger.rides
    qs = qs.filter(state=ride.COMPLETED)
    qs = qs.filter(created_at__startswith=ride.created_at.date())

    if qs.count() == 2:
        Transaction.objects.create(
            user=passenger,
            ride=ride,
            transaction_type=Transaction.MILEAGE,
            amount=settings.POINTS_BY_TYPE['mileage_double_ride'],
            note=u'보너스 마일리지 (1일 2회 이상 탑승)',
        )

    # Add ride count
    passenger.ride_count += 1
    passenger.save()

    # For driver
    driver = ride.driver 

    # Add ride count, deduct call fee
    driver.ride_count += 1
    driver.deposit -= settings.CALL_FEE
    driver.save()   
    
post_create.connect(on_post_create_recommend, sender=Recommend,
                    dispatch_uid='from_payment')
post_ride_complete.connect(on_post_ride_complete, dispatch_uid='from_payment')
