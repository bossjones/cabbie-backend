# encoding: utf8

from cabbie.apps.drive.models import RideHistory
from cabbie.apps.stats.models import DriverRideStat
from cabbie.common.signals import post_create


def on_post_create_ride_history(sender, instance, **kwargs):
    DriverRideStat.objects.sync(instance)


post_create.connect(on_post_create_ride_history, sender=RideHistory,
                    dispatch_uid='from_stats')
