# encoding: utf8
import operator

from django.db import models

from cabbie.apps.account.models import User, Driver
from cabbie.apps.drive.models import Ride
from cabbie.apps.stats.managers import DriverRideStatMonthManager, DriverRideStatWeekManager, DriverRideStatDayManager
from cabbie.common.models import AbstractTimestampModel
from cabbie.common.fields import JSONField

class AbstractRideStatModel(AbstractTimestampModel):
    state = models.CharField(u'상태', max_length=100)
    ratings = JSONField(u'탑승 평점', default='{}') 
    rides = JSONField(u'탑승건', default='[]')

    # property state_kor
    def _state_kor(self):
        return Ride.STATE_EXPRESSION[self.state]
    _state_kor.short_description = u'상태'
    state_kor = property(_state_kor)

    # property count
    def _count(self):
        return len(self.rides)
    _count.short_description = u'횟수'
    count = property(_count)

    # property rating
    def _rating(self):
        value = 0
        count = 0

        for category in ['kindness', 'cleanliness', 'security']:
            v, c = self._ratings_by_category(category)
            value += v
            count += c

        return 0.0 if count == 0 else float(value)/count

    _rating.short_description = u'평점'
    rating = property(_rating)

    def _ratings_by_category(self, category):
        value = 0
        count = 0

        for rating in self.ratings.itervalues():
            point = rating.get(category, None)
            if point:
                value += point
                count += 1
        
        return (value, count)

    # kindness
    def _rating_value_kindness(self):
        return self._ratings_by_category('kindness')[0]
    _rating_value_kindness.short_description = u'친절 총점' 
    rating_value_kindness = property(_rating_value_kindness)

    def _rating_count_kindness(self):
        return self._ratings_by_category('kindness')[1]
    _rating_count_kindness.short_description = u'친절 총수' 
    rating_count_kindness = property(_rating_count_kindness)

    # cleanliness
    def _rating_value_cleanliness(self):
        return self._ratings_by_category('cleanliness')[0]
    _rating_value_cleanliness.short_description = u'청결 총점' 
    rating_value_cleanliness = property(_rating_value_cleanliness)

    def _rating_count_cleanliness(self):
        return self._ratings_by_category('cleanliness')[1]
    _rating_count_cleanliness.short_description = u'청결 평가수' 
    rating_count_cleanliness = property(_rating_count_cleanliness)
 
    # security 
    def _rating_value_security(self):
        return self._ratings_by_category('security')[0]
    _rating_value_security.short_description = u'안전 총점' 
    rating_value_security = property(_rating_value_security)

    def _rating_count_security(self):
        return self._ratings_by_category('security')[1]
    _rating_count_security.short_description = u'안전 총수' 
    rating_count_security = property(_rating_count_security)

               

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

from cabbie.apps.stats.receivers import *
