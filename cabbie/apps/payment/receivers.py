# encoding: utf8

from django.conf import settings

from cabbie.apps.recommend.models import Recommend
from cabbie.apps.payment.models import Transaction, DriverCoupon
from cabbie.apps.payment.signals import return_processed, coupon_processed
from cabbie.apps.drive.signals import post_ride_board, post_ride_first_rated
from cabbie.common.signals import post_create
from cabbie.utils.sms import send_sms


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


def on_post_create_transaction(sender, instance, **kwargs):
    transaction = instance
    if transaction.transaction_type == Transaction.RETURN:
        return

    role = transaction.user.concrete
    return_, created = role.returns.get_or_create(
        is_processed=False)
    return_.amount = role.point
    return_.save(update_fields=['amount'])


def on_post_ride_board(sender, ride, **kwargs):
    amount = settings.POINTS_BY_TYPE.get(Transaction.RIDE_POINT)
    amount = 1000
    if amount:
        Transaction.objects.create(
            user=ride.passenger,
            ride=ride,
            transaction_type=Transaction.RIDE_POINT,
            amount=amount,
            state=Transaction.DONE,
        )

def on_post_ride_first_rated(sender, ride, **kwargs):
    amount = settings.POINTS_BY_TYPE.get(Transaction.RATE_POINT)
    amount = 500
    if amount:
        Transaction.objects.create(
            user=ride.passenger,
            ride=ride,
            transaction_type=Transaction.RATE_POINT,
            amount=amount,
            state=Transaction.DONE,
        )

def on_return_processed(sender, return_, **kwargs):
    return_.user.transactions.create(
        transaction_type=Transaction.RETURN,
        amount=-1 * return_.amount,
        state=Transaction.DONE,
    )
    send_sms('sms/return_processed.txt', return_.user.phone,
             {'return_': return_})


def on_coupon_processed(sender, coupon, **kwargs):
    if coupon.coupon_type == DriverCoupon.GIFTCARD:
        send_sms('sms/coupon_processed.txt', coupon.driver.phone, {'coupon': coupon})
    elif coupon.coupon_type == DriverCoupon.CASH:
        send_sms('sms/cash_processed.txt', coupon.driver.phone, {'coupon': coupon})
        


post_create.connect(on_post_create_recommend, sender=Recommend,
                    dispatch_uid='from_payment')
post_create.connect(on_post_create_transaction, sender=Transaction,
                    dispatch_uid='from_payment')
post_ride_board.connect(on_post_ride_board, dispatch_uid='from_payment')
post_ride_first_rated.connect(on_post_ride_first_rated, dispatch_uid='from_payment')
return_processed.connect(on_return_processed, dispatch_uid='from_payment')
coupon_processed.connect(on_coupon_processed, dispatch_uid='from_payment')
