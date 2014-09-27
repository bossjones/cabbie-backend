# encoding: utf8

from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.utils.translation import ugettext_lazy as _

from cabbie.apps.account.models import Passenger, Driver
from cabbie.apps.drive.signals import post_ride_complete
from cabbie.common.fields import JSONField
from cabbie.common.models import AbstractTimestampModel


class Ride(AbstractTimestampModel):
    REQUESTED, APPROVED, REJECTED, CANCELED, DISCONNECTED, ARRIVED, BOARDED, \
        COMPLETED, RATED = \
    'requested', 'approved', 'rejected', 'canceled', 'disconnected', \
        'arrived', 'boarded', 'completed', 'rated'
    STATES = (
        (REQUESTED, _('requested')),
        (APPROVED, _('approved')),
        (REJECTED, _('rejected')),
        (CANCELED, _('canceled')),
        (DISCONNECTED, _('disconnected')),
        (ARRIVED, _('arrived')),
        (BOARDED, _('boarded')),
        (COMPLETED, _('completed')),
        (RATED, _('rated')),
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
    summary = JSONField(default='{}')

    # Rating
    rating = models.PositiveIntegerField(blank=True, null=True)
    ratings_by_category = JSONField(default='{}')
    comment = models.CharField(max_length=100, blank=True)

    objects = models.GeoManager()

    class Meta(AbstractTimestampModel.Meta):
        verbose_name = u'여정'
        verbose_name_plural = u'여정'

    def transit(self, **data):
        for field in ('state', 'driver_id', 'rating', 'ratings_by_category',
                      'comment', 'summary'):
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

        if self.state == self.COMPLETED:
            post_ride_complete.send(sender=self.__class__, ride=self)


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
