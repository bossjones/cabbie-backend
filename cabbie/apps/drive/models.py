# encoding: utf8
import datetime, time

from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from cabbie.apps.account.models import Passenger, Driver
from cabbie.apps.drive.signals import post_ride_board, post_ride_complete, post_ride_first_rated, post_ride_rated
from cabbie.common.fields import JSONField
from cabbie.common.models import AbstractTimestampModel, IncrementMixin
from cabbie.utils import json
from cabbie.utils.crypto import encrypt
from cabbie.utils.email import send_email


class Ride(IncrementMixin, AbstractTimestampModel):
    REQUESTED, APPROVED, REJECTED, CANCELED, DISCONNECTED, ARRIVED, BOARDED, \
        COMPLETED = \
    'requested', 'approved', 'rejected', 'canceled', 'disconnected', \
        'arrived', 'boarded', 'completed'
    STATES = (
        (REQUESTED, _('requested')),
        (APPROVED, _('approved')),
        (REJECTED, _('rejected')),
        (CANCELED, _('canceled')),
        (DISCONNECTED, _('disconnected')),
        (ARRIVED, _('arrived')),
        (BOARDED, _('boarded')),
        (COMPLETED, _('completed')),
    )

    STATE_EXPRESSION = { 
        REQUESTED: u'요청',
        APPROVED: u'승인',
        REJECTED: u'기사거절',
        CANCELED: u'승객취소',
        DISCONNECTED: u'연결끊김',
        ARRIVED: u'픽업도착',
        BOARDED: u'탑승',
        COMPLETED: u'운행완료',
    }

    IMMEDIATE, TIMEOUT, AFTER, WAITING, UNSHOWN = \
    'immediate', 'timeout', 'after', 'waiting', 'unshown'

    REASONS = (
        (IMMEDIATE, _(u'즉시거절')),
        (TIMEOUT, _(u'수락시간초과')),
        (AFTER, _(u'수락후 거절')),
        (WAITING, _(u'대기중 거절')),
        (UNSHOWN, _(u'승객이 나타나지 않음')),
    )

    passenger = models.ForeignKey(Passenger, related_name='rides',
                                  verbose_name=u'승객')
    driver = models.ForeignKey(Driver, blank=True, null=True,
                               related_name='rides', verbose_name=u'기사')

    state = models.CharField(u'상태', max_length=100, choices=STATES)

    # Reject reason
    reason = models.CharField(u'거절이유', max_length=20, choices=REASONS)

    # Ride detail
    source = JSONField(u'출발지')
    source_location = models.PointField(u'출발지 좌표')
    destination = JSONField(u'도착지', default='{}')
    destination_location = models.PointField(u'도착지 좌표', blank=True,
                                             null=True)
    charge_type = models.PositiveIntegerField(u'콜비', blank=True)
    summary = JSONField(u'요약', default='{}')

    # Rating
    ratings_by_category = JSONField(u'상세평점', default='{}')
    comment = models.CharField(u'코멘트', max_length=100, blank=True)

    objects = models.GeoManager()

    class Meta(AbstractTimestampModel.Meta):
        verbose_name = u'배차'
        verbose_name_plural = u'배차'

    def source_address(self):
        return self.source.get('address', '')
    source_address.short_description = u'출발지 주소'
    source_address = property(source_address)

    def source_poi(self):
        return self.source.get('poi', '')
    source_poi.short_description = u'출발지 POI'
    source_poi = property(source_poi)

    def destination_address(self):
        return self.destination.get('address', '')
    destination_address.short_description = u'도착지 주소'
    destination_address = property(destination_address)

    def destination_poi(self):
        return self.destination.get('poi', '')
    destination_poi.short_description = u'도착지 POI'
    destination_poi = property(destination_poi)

    def get_incrementer(self, reverse=False):
        incrementer = super(Ride, self).get_incrementer(reverse)
        incrementer.add(Passenger, self.passenger_id, 'ride_count')
        if self.driver:
            incrementer.add(Driver, self.driver_id, 'ride_count')
        return incrementer

    @property
    def _created_at_in_local_time(self):
        return timezone.get_current_timezone().normalize(self.created_at)

    # property state_kor
    def _state_kor(self):
        return Ride.STATE_EXPRESSION[self.state]
    _state_kor.short_description = u'상태'
    state_kor = property(_state_kor)


    def rate(self, ratings_by_category, comment):
        old_ratings_by_category = self.ratings_by_category

        self.ratings_by_category = ratings_by_category
        self.comment = comment
        self.save(update_fields=['ratings_by_category', 'comment'])

        self.driver.rate(self.ratings_by_category, old_ratings_by_category)

        # mileage
        if not old_ratings_by_category:
            post_ride_first_rated.send(sender=self.__class__, ride=self)

            send_email('mail/passenger_rating_point.txt', self.passenger.email, 
                {'subject': '탑승평가 포인트 적립', 'message': '백기사를 이용해주셔서 감사합니다. 탑승평가에 대한 포인트를 적립하여 드립니다.'})

        # stat
        post_ride_rated.send(sender=self.__class__, ride=self)

    @property
    def rating(self):
        total_rating = 0

        for key, value in self.ratings_by_category.iteritems():
            total_rating += value

        return 0.0 if len(self.ratings_by_category) == 0 else float(total_rating) / len(self.ratings_by_category)

    def transit(self, **data):
        for field in ('state', 'driver_id', 'charge_type', 'summary', 'reason'):
            value = data.get(field)
            if value:
                setattr(self, field, value)
        self.save()

        passenger_location = (Point(*data['passenger_location'])
                              if 'passenger_location' in data else None)
        driver_location = (Point(*data['driver_location'])
                           if 'driver_location' in data else None)

        self.histories.create(
            driver=self.driver,
            state=self.state,
            passenger_location=passenger_location,
            driver_location=driver_location,
            data=data,
        )

        if self.state == self.BOARDED:
            post_ride_board.send(sender=self.__class__, ride=self)

        if self.state == self.COMPLETED:
            post_ride_complete.send(sender=self.__class__, ride=self)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super(Ride, self).save(
            force_insert, force_update, using, update_fields)


class RideHistory(AbstractTimestampModel):
    ride = models.ForeignKey(Ride, related_name='histories',
                             verbose_name=u'배차')
    driver = models.ForeignKey(Driver, blank=True, null=True,
                               related_name='ride_histories',
                               verbose_name=u'기사')

    state = models.CharField(u'상태', max_length=100, choices=Ride.STATES)
    passenger_location = models.PointField(u'승객 좌표')
    driver_location = models.PointField(u'기사 좌표', blank=True, null=True)
    data = JSONField(u'데이터', default='{}')

    def __unicode__(self):
        return u'Ride {0}: {1}'.format(self.ride.id, self.state)

    class Meta(AbstractTimestampModel.Meta):
        verbose_name = u'배차 이력'
        verbose_name_plural = u'배차 이력'


class Favorite(AbstractTimestampModel):
    passenger = models.ForeignKey(Passenger, related_name='favorites',
                                  verbose_name=u'승객')
    name = models.CharField(u'이름', max_length=100)
    location = models.PointField(u'좌표')
    address = models.CharField(u'주소', max_length=1000, blank=True,
                               db_index=True)
    poi = models.CharField(u'POI', max_length=1000, blank=True)

    objects = models.GeoManager()

    class Meta(AbstractTimestampModel.Meta):
        verbose_name = u'즐겨찾기'
        verbose_name_plural = u'즐겨찾기'


class Hotspot(AbstractTimestampModel):
    location = models.PointField(u'좌표',
                                 help_text=u'경도와 위도를 한줄씩 입력하세요')
    address = models.CharField(u'주소', max_length=1000, blank=True,
                               db_index=True)
    poi = models.CharField(u'POI', max_length=1000, blank=True)
    ride_count = models.PositiveIntegerField(u'배차횟수', default=0)
    weight = models.IntegerField(u'가중치', db_index=True,
                                 help_text=u'높을수록 상위에 노출됩니다')
    is_promotion = models.BooleanField(u'프로모션', default=True)

    class Meta(AbstractTimestampModel.Meta):
        verbose_name = u'인기장소'
        verbose_name_plural = u'인기장소'


from cabbie.apps.drive.receivers import *
