# encoding: utf8

from django.db import models

from cabbie.apps.account.models import User, Driver
from cabbie.apps.stats.managers import DriverRideStatMonthManager, DriverRideStatWeekManager, DriverRideStatDayManager
from cabbie.common.models import AbstractTimestampModel
from cabbie.common.fields import JSONField

class AbstractRideStatModel(AbstractTimestampModel):
    state = models.CharField(u'상태', max_length=100)
    count = models.PositiveIntegerField(u'횟수', default=0)
    ratings = JSONField(u'탑승 평점', default='{}') 

    def _rating(self):
        value = 0
        count = 0

        for rating in self.ratings.itervalues():
            value += sum(rating.itervalues())
            count += len(rating)

        return 0.0 if count == 0 else float(value)/count
    _rating.short_description = u'평점'

    rating = property(_rating)

    class Meta(AbstractTimestampModel.Meta):
        abstract = True
     

class DriverRideStatMonth(AbstractRideStatModel):
    driver = models.ForeignKey(Driver, related_name='monthly_statistics',
                               verbose_name=u'기사')
    year = models.PositiveIntegerField(u'년')
    month = models.PositiveIntegerField(u'월')

    objects = DriverRideStatMonthManager()

    def __unicode__(self):
        return u'RideStatMonth {year}.{month} {state}: ({count}, {rating}) {ratings}'.format(year=self.year, month=self.month, 
                state=self.state, count=self.count, rating=self.rating, ratings=self.ratings)
    
    class Meta(AbstractRideStatModel.Meta):
        verbose_name = u'기사 월별 업무통계'
        verbose_name_plural = u'기사 월별 업무통계'
        unique_together = (
            ('driver', 'year', 'month', 'state'),
        )

class DriverRideStatWeek(AbstractRideStatModel):
    driver = models.ForeignKey(Driver, related_name='weekly_statistics',
                               verbose_name=u'기사')
    year = models.PositiveIntegerField(u'년')
    month = models.PositiveIntegerField(u'월')
    week = models.PositiveIntegerField(u'주')

    objects = DriverRideStatWeekManager()
    
    def __unicode__(self):
        return u'RideStatWeek {year}.{month}.{week} {state}: ({count}, {rating}) {ratings}'.format(year=self.year, month=self.month, week=self.week,
                state=self.state, count=self.count, rating=self.rating, ratings=self.ratings)

    class Meta(AbstractRideStatModel.Meta):
        verbose_name = u'기사 주별 업무통계'
        verbose_name_plural = u'기사 주별 업무통계'
        unique_together = (
            ('driver', 'year', 'month', 'week', 'state'),
        )

class DriverRideStatDay(AbstractRideStatModel):
    driver = models.ForeignKey(Driver, related_name='daily_statistics',
                               verbose_name=u'기사')
    year = models.PositiveIntegerField(u'년')
    month = models.PositiveIntegerField(u'월')
    week = models.PositiveIntegerField(u'주')
    day = models.PositiveIntegerField(u'일')

    objects = DriverRideStatDayManager()
    
    def __unicode__(self):
        return u'RideStatDay {year}.{month}.{week}.{day} {state}: ({count}, {rating}) {ratings}'.format(year=self.year, month=self.month, week=self.week, day=self.day,
                state=self.state, count=self.count, rating=self.rating, ratings=self.ratings)

    class Meta(AbstractRideStatModel.Meta):
        verbose_name = u'기사 일별 업무통계'
        verbose_name_plural = u'기사 일별 업무통계'
        unique_together = (
            ('driver', 'year', 'month', 'week', 'day', 'state'),
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
