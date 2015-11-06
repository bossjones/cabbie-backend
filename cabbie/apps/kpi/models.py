# encoding: utf8
import operator

from django.db import models

from cabbie.apps.account.models import User, Driver
from cabbie.apps.drive.models import Ride
from cabbie.apps.stats.managers import DriverRideStatMonthManager, DriverRideStatWeekManager, DriverRideStatDayManager
from cabbie.common.models import AbstractTimestampModel
from cabbie.common.fields import JSONField

class AbstractKpiModel(AbstractTimestampModel):
    start_filter = models.DateTimeField(u'시작일', null=True)
    end_filter = models.DateTimeField(u'종료일', null=True)

    class Meta(AbstractTimestampModel.Meta):
        abstract = True
     

class PassengerKpiModel(AbstractKpiModel):
    subscriber = models.PositiveIntegerField(u'신규가입자', null=True)
    active_user = models.PositiveIntegerField(u'Active User')
    province = models.CharField(u'시도', max_length=10, default='', null=True, blank=True)
    region = models.CharField(u'지역', max_length=20, default='', null=True, blank=True)
    ride_requested = models.PositiveIntegerField(u'콜요청')
    ride_approved = models.PositiveIntegerField(u'수락')
    ride_canceled = models.PositiveIntegerField(u'승객취소')
    ride_rejected = models.PositiveIntegerField(u'기사거절')
    ride_completed = models.PositiveIntegerField(u'운행완료')
    ride_rated = models.PositiveIntegerField(u'평가완료')
    ride_rate_sum = models.PositiveIntegerField(u'합산평점')
    ride_satisfied = models.PositiveIntegerField(u'4.5이상')

    # by distance
    ride_short = models.PositiveIntegerField(u'0-3km (%)', default=0)
    ride_medium = models.PositiveIntegerField(u'3-6km (%)', default=0)
    ride_long = models.PositiveIntegerField(u'6-10km (%)', default=0)
    ride_xlong = models.PositiveIntegerField(u'10km이상 (%)', default=0)

    class Meta(AbstractKpiModel.Meta):
        ordering = ('id',)
        verbose_name = u'승객 KPI'
        verbose_name_plural = u'승객 KPI'

class DriverKpiModel(AbstractKpiModel):
    subscriber = models.PositiveIntegerField(u'신규가입자')
    rate_sum_of_educated = models.PositiveIntegerField(u'정규교육 이수 기사 평점합계')
    rate_count_of_educated = models.FloatField(u'정규교육 이수 기사 평점수')
    rate_sum_of_uneducated = models.FloatField(u'교육 비이수 기사 평점합계')
    rate_count_of_uneducated = models.FloatField(u'교육 비이수 기사 평점수')

    class Meta(AbstractKpiModel.Meta):
        verbose_name = u'기사 KPI'
        verbose_name_plural = u'기사 KPI'
