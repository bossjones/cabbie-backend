# encoding: utf8
import datetime

from django.conf import settings

from cabbie.apps.account.models import Passenger
from cabbie.apps.recommend.models import Recommend
from cabbie.apps.payment.models import Transaction, DriverCoupon
from cabbie.apps.payment.signals import return_processed, return_apply_completed, coupon_processed
from cabbie.apps.payment import messages
from cabbie.apps.event.models import RidePointEvent
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
            note=u'추천 포인트 (추천)'
        )

    amount = settings.POINTS_BY_TYPE.get(
        'recommended_{0}'.format(recommend.recommend_type))
    if amount:
        Transaction.objects.create(
            user=recommend.recommendee,
            recommend=recommend,
            transaction_type=Transaction.RECOMMENDED,
            amount=amount,
            note=u'추천 포인트 (피추천)'
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

def during_ride_point_event():
    ride_point_event_starts_from = datetime.datetime.strptime(settings.BKTAXI_PASSENGER_RIDE_POINT_PROMOTION_2_3000P_BEGIN, "%Y-%m-%d").date()
    ride_point_event_ends_at = datetime.datetime.strptime(settings.BKTAXI_PASSENGER_RIDE_POINT_PROMOTION_2_3000P_END, "%Y-%m-%d").date()

    today = datetime.date.today()

    return today >= adjusted_ride_point_activated_from 


def on_post_ride_board(sender, ride, **kwargs):
    passenger = ride.passenger
    
    # affiliation ride point
    affiliation_ride_point = 0
    if passenger.is_affiliated:
        affiliation_ride_point = passenger.affiliation.ride_mileage


    # compare "event ride point" with "affiliation ride point"
    current_event = RidePointEvent.current_event() 

    if current_event and current_event.event_point > affiliation_ride_point:
        success = current_event.apply_event(ride)

        if success:
            amount = current_event.event_point 
            Transaction.objects.create(
                user=passenger,
                ride=ride,
                transaction_type=Transaction.RIDE_POINT,
                amount=amount,
                state=Transaction.DONE,
                note=u'이벤트 탑승 포인트'
            )
            return

    # affiliated
    if passenger.is_affiliated:
        # amount
        amount = passenger.affiliation.ride_mileage
        Transaction.objects.create(
            user=passenger,
            ride=ride,
            transaction_type=Transaction.RIDE_POINT,
            amount=amount,
            state=Transaction.DONE,
            note=u'제휴사 회원 탑승 포인트'
        )
    else:
        amount = settings.BKTAXI_PASSENGER_RIDE_POINT_ADJUSTED_AMOUNT
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

    if user.is_email_agreed and isinstance(user, Passenger):
        send_email('mail/point/point_application_completed.html', user.email, {
            # common
            'cdn_url': settings.EMAIL_CDN_DOMAIN_NAME,
            'email_font': settings.EMAIL_DEFAULT_FONT,
            'bktaxi_web_url': settings.BKTAXI_WEB_URL,
            'bktaxi_facebook_url': settings.BKTAXI_FACEBOOK_URL,
            'bktaxi_instagram_url': settings.BKTAXI_INSTAGRAM_URL,
            'bktaxi_naver_blog_url': settings.BKTAXI_NAVER_BLOG_URL,

            'subject': messages.PAYMENT_EMAIL_SUBJECT_POINT_APPLICATION_COMPLETED, 
            'return': return_, 
        })

def on_return_processed(sender, return_, **kwargs):
    return_.user.transactions.create(
        transaction_type=Transaction.RETURN,
        amount=-1 * return_.amount,
        state=Transaction.DONE,
        note=Transaction.get_transaction_type_text(Transaction.RETURN)
    )
    
    user = return_.user.concrete

    if user.is_email_agreed and isinstance(user, Passenger):
        send_email('mail/point/point_application_processed.html', user.email, {
            # common
            'cdn_url': settings.EMAIL_CDN_DOMAIN_NAME,
            'email_font': settings.EMAIL_DEFAULT_FONT,
            'bktaxi_web_url': settings.BKTAXI_WEB_URL,
            'bktaxi_facebook_url': settings.BKTAXI_FACEBOOK_URL,
            'bktaxi_instagram_url': settings.BKTAXI_INSTAGRAM_URL,
            'bktaxi_naver_blog_url': settings.BKTAXI_NAVER_BLOG_URL,

            'subject': messages.PAYMENT_EMAIL_SUBJECT_POINT_APPLICATION_PROCESSED, 
            'return': return_, 
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
