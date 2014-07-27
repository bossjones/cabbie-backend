from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _

from cabbie.apps.account.models import Passenger, Driver
from cabbie.common.models import AbstractTimestampModel


class Ride(AbstractTimestampModel):
    INITIATED, REQUESTED, APPROVED, REJECTED, CANCELED, \
        ARRIVED, BOARDED, COMPLETED, PAID = \
    'initiated', 'requested', 'approved', 'rejected', 'canceled', \
        'arrived', 'boarded', 'completed', 'paid'
    STATES = (
        (INITIATED, _('initiated')),
        (REQUESTED, _('requested')),
        (APPROVED, _('approved')),
        (REJECTED, _('rejected')),
        (CANCELED, _('canceled')),
        (ARRIVED, _('arrived')),
        (BOARDED, _('boarded')),
        (COMPLETED, _('completed')),
        (PAID, _('paid')),
    )

    passenger = models.ForeignKey(Passenger, related_name='rides')
    driver = models.ForeignKey(Driver, blank=True, null=True,
                               related_name='rides')

    state = models.CharField(max_length=100, choices=STATES)
    source = models.PointField()
    destination = models.PointField(blank=True, null=True)

    objects = models.GeoManager()


class RideHistory(AbstractTimestampModel):
    ride = models.ForeignKey(Ride, related_name='histories')
    driver = models.ForeignKey(Driver, blank=True, null=True)

    state = models.CharField(max_length=100, choices=Ride.STATES)
    passenger_location = models.PointField()
    driver_location = models.PointField(blank=True, null=True)

    # FIXME: Extra data
