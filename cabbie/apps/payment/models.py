# encoding: utf8

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from cabbie.apps.account.models import Passenger, Driver
from cabbie.apps.drive.models import Ride
from cabbie.apps.recommend.models import Recommend
from cabbie.common.models import IncrementMixin, AbstractTimestampModel


class DriverBill(AbstractTimestampModel):
    driver = models.ForeignKey(Driver, related_name='bills')
    amount = models.PositiveIntegerField()

    class Meta(AbstractTimestampModel.Meta):
        verbose_name = u'기사 사용료'
        verbose_name_plural = u'기사 사용료'


class DriverCoupon(AbstractTimestampModel):
    GAS, = ('gas',)

    COUPON_TYPES = (
        (GAS, u'LPG 충전권'),
    )

    driver = models.ForeignKey(Driver, related_name='coupons')
    coupon_type = models.CharField(max_length=100, db_index=True,
                                    choices=COUPON_TYPES)
    amount = models.PositiveIntegerField(null=True, blank=True)
    serial_number = models.CharField(max_length=100, blank=True)

    class Meta(AbstractTimestampModel.Meta):
        verbose_name = u'기사 쿠폰'
        verbose_name_plural = u'기사 쿠폰'


class Transaction(IncrementMixin, AbstractTimestampModel):
    MILEAGE, RETURN, RECOMMEND, RECOMMENDED, GRANT = (
        'mileage', 'return', 'recommend', 'recommended', 'grant')

    TRANSACTION_TYPES = (
        (MILEAGE, u'마일리지'),
        (RETURN, u'환급'),
        (RECOMMEND, u'추천'),
        (RECOMMENDED, u'피추천'),
        (GRANT, u'지급'),
    )

    user_content_type = models.ForeignKey(ContentType)
    user_object_id = models.PositiveIntegerField()
    user = GenericForeignKey('user_content_type', 'user_object_id')

    ride = models.ForeignKey(Ride, blank=True, null=True,
                             related_name='transactions')
    recommend = models.ForeignKey(Recommend, blank=True, null=True,
                                  related_name='transactions')
    transaction_type = models.CharField(max_length=100, db_index=True,
                                        choices=TRANSACTION_TYPES)
    amount = models.IntegerField()
    note = models.CharField(max_length=1000, blank=True)

    class Meta(AbstractTimestampModel.Meta):
        verbose_name = u'포인트 사용내역'
        verbose_name_plural = u'포인트 사용내역'

    def get_incrementer(self, reverse=False):
        return (super(Transaction, self).get_incrementer(reverse)
                .add(self.user.__class__, self.user_object_id, 'point',
                     self.amount))


from cabbie.apps.payment.receivers import *
