from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _

from cabbie.apps.account.models import User
from cabbie.common.models import ActiveMixin, AbstractTimestampModel


# Abstract
# --------

class AbstractRole(ActiveMixin, AbstractTimestampModel):
    user = models.OneToOneField(User, related_name='%(class)s')

    class Meta(AbstractTimestampModel.Meta):
        abstract = True

    def __unicode__(self):
        return self.user.__unicode__()


# Concrete
# --------

class Passenger(AbstractRole):
    ride_count = models.PositiveIntegerField(default=0)


class Driver(AbstractRole):
    licence_number = models.CharField(max_length=100, unique=True)
    ride_count = models.PositiveIntegerField(default=0)


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
