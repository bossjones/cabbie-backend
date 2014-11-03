# encoding: utf8

from django.db import models

from cabbie.apps.account.models import User, Driver
from cabbie.apps.stats.managers import DriverRideStatManager
from cabbie.common.models import AbstractTimestampModel


class DriverRideStat(AbstractTimestampModel):
    driver = models.ForeignKey(Driver, related_name='ride_stats',
                               verbose_name=u'기사')
    year = models.PositiveIntegerField()
    month = models.PositiveIntegerField()
    week = models.PositiveIntegerField()
    state = models.CharField(max_length=100)
    count = models.PositiveIntegerField(default=0)

    objects = DriverRideStatManager()

    class Meta(AbstractTimestampModel.Meta):
        verbose_name = u'기사 업무통계'
        verbose_name_plural = u'기사 업무통계'
        unique_together = (
            ('driver', 'year', 'month', 'week', 'state'),
        )


class LocationDataAccess(AbstractTimestampModel):
    user = models.ForeignKey(User, related_name='location_data_accesses',
                             verbose_name=u'접근한 사용자')

    class Meta(AbstractTimestampModel.Meta):
        verbose_name = u'위치정보 접근로그'
        verbose_name_plural = u'위치정보 접근로그'


class LocationDataProvide(AbstractTimestampModel):
    provider = models.ForeignKey(
        User, related_name='location_data_provider_history',
        verbose_name=u'제공한자')
    providee = models.ForeignKey(
        User, related_name='location_data_providee_history',
        null=True, blank=True, verbose_name=u'제공받은자')
    provider_type = models.CharField(max_length=20, verbose_name=u'취득경로')
    service = models.CharField(max_length=20, verbose_name=u'제공서비스')

    class Meta(AbstractTimestampModel.Meta):
        verbose_name = u'위치정보 이용제공내역'
        verbose_name_plural = u'위치정보 이용제공내역'


class LocationDataNotice(AbstractTimestampModel):
    noticer = models.ForeignKey(
        User, related_name='location_data_noticer_history',
        verbose_name=u'취급자')
    requester = models.ForeignKey(
        User, related_name='location_data_requester_history',
        verbose_name=u'요청자')
    purpose = models.CharField(max_length=100, verbose_name=u'목적')

    class Meta(AbstractTimestampModel.Meta):
        verbose_name = u'위치정보 열람및고지내역'
        verbose_name_plural = u'위치정보 열람및고지내역'


from cabbie.apps.stats.receivers import *
