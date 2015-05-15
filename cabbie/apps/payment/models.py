# encoding: utf8

from django.db import models
from django.utils import timezone

from cabbie.apps.account.models import User, Passenger, Driver
from cabbie.apps.drive.models import Ride
from cabbie.apps.payment.signals import return_processed, return_apply_completed, coupon_processed
from cabbie.apps.recommend.models import Recommend
from cabbie.common.models import IncrementMixin, AbstractTimestampModel


class DriverBill(AbstractTimestampModel):
    driver = models.ForeignKey(Driver, related_name='bills',
                               verbose_name=u'기사')
    target_month = models.CharField(max_length=6, help_text=u'e.g. 201409')
    amount = models.PositiveIntegerField(u'금액')

    class Meta(AbstractTimestampModel.Meta):
        verbose_name = u'기사 사용료'
        verbose_name_plural = u'기사 사용료'


class DriverCoupon(AbstractTimestampModel):
    GIFTCARD, CASH = ('giftcard', 'cash')

    COUPON_TYPES = (
        (CASH, u'현금'),
        (GIFTCARD, u'상품권'),
    )

    driver = models.ForeignKey(Driver, related_name='coupons',
                               verbose_name=u'기사')
    coupon_type = models.CharField(u'리워드 종류', max_length=100, db_index=True,
                                   choices=COUPON_TYPES, default=CASH)
    coupon_name = models.CharField(u'리워드명', max_length=100, null=True, blank=True)
    amount = models.PositiveIntegerField(u'금액', null=True, blank=True)
    serial_number = models.CharField(u'쿠폰일련번호', max_length=100,
                                     blank=True)
    is_processed = models.BooleanField(u'지급완료여부', default=False)
    processed_at = models.DateTimeField(u'지급시점', null=True, blank=True)

    class Meta(AbstractTimestampModel.Meta):
        verbose_name = u'기사 리워드'
        verbose_name_plural = u'기사 리워드'

    def previous_month_board_count(self):
        return self.driver.previous_month_board_count
    previous_month_board_count.short_description = u'전월 콜횟수'
    previous_month_board_count = property(previous_month_board_count)

    def process(self):
        if self.is_processed:
            return
        self.is_processed = True
        self.processed_at = timezone.now()
        self.save(update_fields=['is_processed', 'processed_at'])

        coupon_processed.send(sender=self.__class__, coupon=self)


class Transaction(IncrementMixin, AbstractTimestampModel):
    SIGNUP_POINT, RIDE_POINT, RATE_POINT, RECOMMEND, RECOMMENDED, GRANT, RETURN = (
        'signup_point', 'ride_point', 'rate_point', 'recommend', 'recommended', 'grant', 'return')

    TRANSACTION_TYPES = (
        (SIGNUP_POINT, u'신규가입 포인트'),
        (RIDE_POINT, u'탑승 포인트'),
        (RATE_POINT, u'평가 포인트'),
        (RECOMMEND, u'추천'),
        (RECOMMENDED, u'피추천'),
        (GRANT, u'지급'),
        (RETURN, u'환급'),
    )

    PLANNED, DONE = ('planned', 'done')

    TRANSACTION_STATES = (
        (PLANNED, u'예정'),
        (DONE, u'완료'),
    )

    user = models.ForeignKey(User, related_name='transactions',
                             verbose_name=u'사용자')
    ride = models.ForeignKey(Ride, blank=True, null=True,
                             related_name='transactions', verbose_name=u'콜', on_delete=models.SET_NULL)
    recommend = models.ForeignKey(Recommend, blank=True, null=True,
                                  related_name='transactions',
                                  verbose_name=u'추천', on_delete=models.SET_NULL)
    transaction_type = models.CharField(u'종류', max_length=100, db_index=True,
                                        choices=TRANSACTION_TYPES)
    amount = models.IntegerField(u'금액')
    state = models.CharField(u'상태', max_length=30, choices=TRANSACTION_STATES, default=PLANNED)
    note = models.CharField(u'메모', max_length=1000, blank=True)

    class Meta(AbstractTimestampModel.Meta):
        verbose_name = u'포인트 이력'
        verbose_name_plural = u'포인트 이력'

    def get_incrementer(self, reverse=False):
        return (super(Transaction, self).get_incrementer(reverse)
                .add(self.user.__class__, self.user_id, 'point', self.amount))
    
    @staticmethod
    def get_transaction_type_text(transaction_type):
        return dict(Transaction.TRANSACTION_TYPES).get(transaction_type)

class AbstractReturn(AbstractTimestampModel):
    amount = models.PositiveIntegerField(u'환급액', default=0)
    is_requested = models.BooleanField(u'환급요청정보 기입여부', default=False)
    is_processed = models.BooleanField(u'환급완료여부', default=False)
    processed_at = models.DateTimeField(u'환급시점', null=True, blank=True)
    note = models.CharField(u'메모', max_length=1000, blank=True)

    class Meta(AbstractTimestampModel.Meta):
        abstract = True

    def phone(self):
        return self.user.phone
    phone.short_description = u'전화번호'
    phone = property(phone)

    def bank_account(self):
        return self.user.bank_account
    bank_account.short_description = u'은행계좌'
    bank_account = property(bank_account)

    def mark_as_requested(self):
        if self.is_requested:
            return
        self.is_requested = True
        self.save(update_fields=['is_requested'])

        return_apply_completed.send(sender=self.__class__, return_=self)

    def process(self):
        if self.is_processed:
            return
        self.is_processed = True
        self.processed_at = timezone.now()
        self.save(update_fields=['is_processed', 'processed_at'])

        return_processed.send(sender=self.__class__, return_=self)


class PassengerReturn(AbstractReturn):
    user = models.ForeignKey(Passenger, related_name='returns',
                             verbose_name=u'승객')
    class Meta(AbstractReturn.Meta):
        verbose_name = u'승객 환급금'
        verbose_name_plural = u'승객 환급금'


class DriverReturn(AbstractReturn):
    user = models.ForeignKey(Driver, related_name='returns',
                             verbose_name=u'기사')
    class Meta(AbstractReturn.Meta):
        verbose_name = u'기사 환급금'
        verbose_name_plural = u'기사 환급금'


from cabbie.apps.payment.receivers import *
