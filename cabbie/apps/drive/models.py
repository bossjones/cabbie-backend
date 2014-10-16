# encoding: utf8

from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.utils.translation import ugettext_lazy as _

from cabbie.apps.account.models import Passenger, Driver
from cabbie.apps.drive.signals import post_ride_board
from cabbie.common.fields import JSONField
from cabbie.common.models import AbstractTimestampModel
from cabbie.utils import json
from cabbie.utils.crypto import encrypt
from cabbie.utils.increment import Incrementer



class Ride(AbstractTimestampModel):
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

    passenger = models.ForeignKey(Passenger, related_name='rides')
    driver = models.ForeignKey(Driver, blank=True, null=True,
                               related_name='rides')

    state = models.CharField(max_length=100, choices=STATES)

    # Ride detail
    source = JSONField()
    source_location = models.PointField()
    destination = JSONField(default='{}')
    destination_location = models.PointField(blank=True, null=True)
    charge_type = models.CharField(max_length=100, blank=True)
    summary = JSONField(default='{}')

    # Encryption
    source_encrypted = models.CharField(max_length=1000, blank=True)
    source_location_encrypted = models.CharField(max_length=1000, blank=True)
    destination_encrypted = models.CharField(max_length=1000, blank=True)
    destination_location_encrypted = models.CharField(max_length=1000,
                                                     blank=True)

    # Rating
    rating = models.PositiveIntegerField(blank=True, null=True)
    ratings_by_category = JSONField(default='{}')
    comment = models.CharField(max_length=100, blank=True)

    objects = models.GeoManager()

    class Meta(AbstractTimestampModel.Meta):
        verbose_name = u'여정'
        verbose_name_plural = u'여정'

    def rate(self, rating, ratings_by_category):
        if self.state not in (self.BOARDED, self.COMPLETED):
            raise Exception(u'탑승 또는 여정 완료 후 평가가 가능합니다')

        if self.rating is not None:
            raise Exception(u'이미 평가된 상태입니다')

        self.rating = rating
        self.ratings_by_category = ratings_by_category
        self.save(update_fields=['rating', 'ratings_by_category'])

        (Incrementer()
            .add(Driver, self.driver_id, 'rated_count')
            .add(Driver, self.driver_id, 'total_rating', self.rating)).run()

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

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        for field in ('source', 'destination'):
            value = getattr(self, field, None)
            if value:
                encrypted = encrypt(json.dumps(value))
                encrypted_field = '{0}_encrypted'.format(field)
                setattr(self, encrypted_field, encrypted)
                if update_fields:
                    update_fields.append(field)

        for field in ('source_location', 'destination_location'):
            value = getattr(self, field, None)
            if value:
                encrypted = encrypt(json.dumps(value.coords))
                encrypted_field = '{0}_encrypted'.format(field)
                setattr(self, encrypted_field, encrypted)
                if update_fields:
                    update_fields.append(field)

        super(Ride, self).save(
            force_insert, force_update, using, update_fields)


class RideHistory(AbstractTimestampModel):
    ride = models.ForeignKey(Ride, related_name='histories')
    driver = models.ForeignKey(Driver, blank=True, null=True,
                               related_name='ride_histories')

    state = models.CharField(max_length=100, choices=Ride.STATES)
    passenger_location = models.PointField()
    driver_location = models.PointField(blank=True, null=True)
    data = JSONField(default='{}')

    class Meta(AbstractTimestampModel.Meta):
        verbose_name = u'여정 이력'
        verbose_name_plural = u'여정 이력'


class Favorite(AbstractTimestampModel):
    passenger = models.ForeignKey(Passenger, related_name='favorites')
    name = models.CharField(max_length=100)
    location = models.PointField()
    address = models.CharField(max_length=1000, blank=True, db_index=True)
    poi = models.CharField(max_length=1000, blank=True)

    objects = models.GeoManager()

    class Meta(AbstractTimestampModel.Meta):
        verbose_name = u'즐겨찾기'
        verbose_name_plural = u'즐겨찾기'
