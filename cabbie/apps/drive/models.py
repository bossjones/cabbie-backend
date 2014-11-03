# encoding: utf8

from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.utils.translation import ugettext_lazy as _

from cabbie.apps.account.models import Passenger, Driver
from cabbie.apps.drive.signals import post_ride_board, post_ride_complete
from cabbie.common.fields import JSONField
from cabbie.common.models import AbstractTimestampModel, IncrementMixin
from cabbie.utils import json
from cabbie.utils.crypto import encrypt


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

    passenger = models.ForeignKey(Passenger, related_name='rides',
                                  verbose_name=u'승객')
    driver = models.ForeignKey(Driver, blank=True, null=True,
                               related_name='rides', verbose_name=u'기사')

    state = models.CharField(u'상태', max_length=100, choices=STATES)

    # Ride detail
    source = JSONField(u'출발지')
    source_location = models.PointField(u'출발지 좌표')
    destination = JSONField(u'도착지', default='{}')
    destination_location = models.PointField(u'도착지 좌표', blank=True,
                                             null=True)
    charge_type = models.CharField(u'콜비', max_length=100, blank=True)
    summary = JSONField(u'요약', default='{}')

    # Rating
    rating = models.PositiveIntegerField(u'평점', blank=True, null=True)
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

    def rate(self, rating, ratings_by_category, comment):
        if self.state not in (self.BOARDED, self.COMPLETED):
            raise Exception(u'콜 완료 후 평가가 가능합니다')

        if self.rating is not None:
            raise Exception(u'이미 평가된 상태입니다')

        self.rating = rating
        self.ratings_by_category = ratings_by_category
        self.comment = comment
        self.save(update_fields=['rating', 'ratings_by_category', 'comment'])

        self.driver.rate(self.rating)

    def transit(self, **data):
        for field in ('state', 'driver_id', 'charge_type', 'summary'):
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
