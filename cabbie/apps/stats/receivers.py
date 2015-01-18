# encoding: utf8

from cabbie.apps.drive.models import Ride, RideHistory
from cabbie.apps.drive.signals import post_ride_rated
from cabbie.apps.stats.models import DriverRideStatMonth, DriverRideStatWeek, DriverRideStatDay
from cabbie.common.signals import post_create, post_delete


def on_post_create_ride_history(sender, instance, **kwargs):
    DriverRideStatDay.objects.sync(instance)
    DriverRideStatWeek.objects.sync(instance)
    DriverRideStatMonth.objects.sync(instance)

def on_post_ride_rated(sender, ride, **kwargs):
    DriverRideStatDay.objects.sync_rate(ride)
    DriverRideStatWeek.objects.sync_rate(ride)
    DriverRideStatMonth.objects.sync_rate(ride)

def on_post_delete_ride_history(sender, instance, **kwargs):
    if not instance.driver:
        return

    for stat_class in (DriverRideStatMonth, DriverRideStatWeek, DriverRideStatDay):
        for stat in stat_class.objects.filter(driver=instance.driver, state=instance.state).all():
            stat._remove_rating(instance.ride.id)
            stat._remove_ride(instance.ride.id)
            stat.save(update_fields=['ratings', 'rides'])

        for stat in stat_class.objects.filter(driver=instance.driver, state=Ride.RATED).all():
            stat._remove_rating(instance.ride.id)
            stat._remove_ride(instance.ride.id)
            stat.save(update_fields=['ratings', 'rides'])
         

    # update rating in driver account, only done from month stat
    instance.driver._update_rating()

post_create.connect(on_post_create_ride_history, sender=RideHistory,
                    dispatch_uid='from_stats')
post_ride_rated.connect(on_post_ride_rated, dispatch_uid='from_stats') 

post_delete.connect(on_post_delete_ride_history, sender=RideHistory,
                    dispatch_uid='from_stats')
