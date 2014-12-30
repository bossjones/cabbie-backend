# encoding: utf8

from cabbie.apps.drive.models import RideHistory
from cabbie.apps.drive.signals import post_ride_rated
from cabbie.apps.stats.models import DriverRideStatMonth, DriverRideStatWeek, DriverRideStatDay
from cabbie.common.signals import post_create


def on_post_create_ride_history(sender, instance, **kwargs):
    DriverRideStatDay.objects.sync(instance)
    DriverRideStatWeek.objects.sync(instance)
    DriverRideStatMonth.objects.sync(instance)

def on_post_ride_rated(sender, ride, **kwargs):
    DriverRideStatDay.objects.sync_rate(ride)
    DriverRideStatWeek.objects.sync_rate(ride)
    DriverRideStatMonth.objects.sync_rate(ride)

post_create.connect(on_post_create_ride_history, sender=RideHistory,
                    dispatch_uid='from_stats')
post_ride_rated.connect(on_post_ride_rated, dispatch_uid='from_stats') 


