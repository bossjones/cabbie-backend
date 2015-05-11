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
    subscriber = models.PositiveIntegerField(u'신규가입자')
    active_user = models.PositiveIntegerField(u'Active User')
    ride_requested = models.PositiveIntegerField(u'콜요청')
    ride_approved = models.PositiveIntegerField(u'수락')
    ride_canceled = models.PositiveIntegerField(u'승객취소')
    ride_rejected = models.PositiveIntegerField(u'기사거절')
    ride_completed = models.PositiveIntegerField(u'운행완료')
    ride_rated = models.PositiveIntegerField(u'평가완료')
    ride_satisfied = models.PositiveIntegerField(u'4.5이상')

    class Meta(AbstractKpiModel.Meta):
        verbose_name = u'승객 KPI'
        verbose_name_plural = u'승객 KPI'


