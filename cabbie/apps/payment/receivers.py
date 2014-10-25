# encoding: utf8

from django.conf import settings

from cabbie.apps.recommend.models import Recommend
from cabbie.apps.drive.signals import post_ride_board
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


def on_post_ride_board(sender, ride, **kwargs):
    # For passenger
    passenger = ride.passenger
    note = u''

    # Peak day mileage
    if ride.is_non_peak_day:
        amount = settings.POINTS_BY_TYPE['mileage_non_peak_day']
        note = u'논피크요일 마일리지 적용'
    # Non-peak day mileage 
    else:
        amount = settings.POINTS_BY_TYPE['mileage']

    Transaction.objects.create(
        user=passenger,
        ride=ride,
        transaction_type=Transaction.MILEAGE,
        amount=amount,
        note=note,
    )

    # For driver
    
    # Rebate for peak time
    if ride.is_peak_hour and ride.is_rebate:
        driver = ride.driver
        amount = settings.POINTS_BY_TYPE['rebate']
        note = u'피크시간 지원금'
     
        Transaction.objects.create(
            user=driver,
            ride=ride,
            transaction_type=Transaction.GRANT,
            amount=amount,
            note=note,
        )

   

post_create.connect(on_post_create_recommend, sender=Recommend,
                    dispatch_uid='from_payment')
post_ride_board.connect(on_post_ride_board, dispatch_uid='from_payment')
