# encoding: utf8

from django.conf import settings

from cabbie.apps.account.models import Passenger
from cabbie.apps.recommend.models import Recommend
from cabbie.apps.payment.models import Transaction, DriverCoupon
from cabbie.apps.payment.signals import return_processed, return_apply_completed, coupon_processed
from cabbie.apps.drive.signals import post_ride_board, post_ride_first_rated
from cabbie.common.signals import post_create
from cabbie.utils.sms import send_sms
from cabbie.utils.email import send_email


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

# deprecated 
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
    if amount:
        Transaction.objects.create(
            user=ride.passenger,
            ride=ride,
            transaction_type=Transaction.RIDE_POINT,
            amount=amount,
            state=Transaction.DONE,
            note=Transaction.get_transaction_type_text(Transaction.RIDE_POINT)
        )

def on_post_ride_first_rated(sender, ride, **kwargs):
    amount = settings.POINTS_BY_TYPE.get(Transaction.RATE_POINT)
    if amount and amount > 0:
        Transaction.objects.create(
            user=ride.passenger,
            ride=ride,
            transaction_type=Transaction.RATE_POINT,
            amount=amount,
            state=Transaction.DONE,
            note=Transaction.get_transaction_type_text(Transaction.RATE_POINT)
        )

def on_return_apply_completed(sender, return_, **kwargs):
    user = return_.user.concrete

    if isinstance(user, Passenger):
        send_email('mail/point/return_apply_completed.txt', user.email, {
            'subject': u'[백기사] 포인트 환급 신청 접수 완료',
            'message': u'{created_at} 요청하신 환급 신청 접수가 완료되었습니다. {amount}포인트 환급완료'
                        .format(created_at=return_.created_at, amount=return_.amount),
        })

def on_return_processed(sender, return_, **kwargs):
    return_.user.transactions.create(
        transaction_type=Transaction.RETURN,
        amount=-1 * return_.amount,
        state=Transaction.DONE,
        note=Transaction.get_transaction_type_text(Transaction.RETURN)
    )
    
    user = return_.user.concrete

    if isinstance(user, Passenger):
        send_email('mail/point/return_processed.txt', user.email, {
            'subject': u'[백기사] 포인트가 환급 완료되었습니다.',
            'message': u'{created_at} 요청하신 {amount}포인트 환급완료'
                        .format(created_at=return_.created_at, amount=return_.amount),
        })


def on_coupon_processed(sender, coupon, **kwargs):
    if coupon.coupon_type == DriverCoupon.GIFTCARD:
        send_sms('sms/coupon_processed.txt', coupon.driver.phone, {'coupon': coupon})
    elif coupon.coupon_type == DriverCoupon.CASH:
        send_sms('sms/cash_processed.txt', coupon.driver.phone, {'coupon': coupon})
        


post_create.connect(on_post_create_recommend, sender=Recommend,
                    dispatch_uid='from_payment')
post_ride_board.connect(on_post_ride_board, dispatch_uid='from_payment')
post_ride_first_rated.connect(on_post_ride_first_rated, dispatch_uid='from_payment')
return_processed.connect(on_return_processed, dispatch_uid='from_payment')
return_apply_completed.connect(on_return_apply_completed, dispatch_uid='from_payment')
coupon_processed.connect(on_coupon_processed, dispatch_uid='from_payment')
