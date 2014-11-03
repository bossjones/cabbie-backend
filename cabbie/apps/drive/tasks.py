from collections import Counter
import datetime

from celery.task import Task
from django.conf import settings
from django.contrib.gis.geos import Point
from django.utils import timezone

from cabbie.apps.drive.models import Ride, Hotspot


class ComputeHotspotDailyTask(Task):
    def run(self, *args, **kwargs):
        yesterday = timezone.now().date() - datetime.timedelta(days=1)
        # FIXME
        yesterday = timezone.now().date()
        dt_range = (
            datetime.datetime.combine(yesterday, datetime.time.min),
            datetime.datetime.combine(yesterday, datetime.time.max),
        )

        counter = Counter()
        points = {}

        for ride in Ride.objects.filter(created_at__range=dt_range):
            source = ride.source
            location = tuple(source['location'])
            counter[location] += 1
            if location not in points:
                points[location] = source

        Hotspot.objects.filter(is_promotion=False).delete()
        remaining_hotspot_count = Hotspot.objects.all().count()
        target_hotspot_count = settings.HOTSPOT_COUNT - remaining_hotspot_count

        for location, count in counter.most_common()[:target_hotspot_count]:
            point = points[location]
            hotspot, created = Hotspot.objects.get_or_create(
                location=Point(*location), defaults={
                    'address': point.get('address') or '',
                    'poi': point.get('poi') or '',
                    'is_promotion': False,
                    'weight': count,
                })
            hotspot.ride_count = count
            hotspot.save(update_fields=['ride_count'])
