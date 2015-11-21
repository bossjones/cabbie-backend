from collections import Counter
import datetime

from celery.task import Task
from django.conf import settings
from django.contrib.gis.geos import Point
from django.utils import timezone

from cabbie.apps.drive.models import Province, Region, Request, RequestNormalized, Ride, Hotspot


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


class UpdateRequestRegionsTask(Task):
    def run(self, *args, **kwargs):
        requests = Request.objects.exclude(source={}).filter(destination_province=None) 
        
        for request in requests:
            source_province, source_region1, source_region2 = request.parse_source()    # source_region2 is nullable 
            destination_province, destination_region1, destination_region2 = request.parse_destination()    # destination_region2 is nullable
            
            update_fields = [] 
            # update Province, Region, Request
            # -----------------------

            # source
            # 1. create Province, Region
            source_province_obj, created = Province.objects.get_or_create(name=source_province)
            source_region1_obj, created = Region.objects.get_or_create(name=source_region1, depth=1, province=source_province_obj)

            # 2. update Request
            request.source_province = source_province_obj
            request.source_region1 = source_region1_obj
            update_fields.append('source_province')
            update_fields.append('source_region1')

            # 3. region2 needs null check
            if source_region2:
                source_region2_obj, created = Region.objects.get_or_create(name=source_region2, depth=2, province=source_province_obj, parent=source_region1_obj)
                request.source_region2 = source_region2_obj
                update_fields.append('source_region2')

            # destination
            # 1. create Province, Region
            destination_province_obj, created = Province.objects.get_or_create(name=destination_province)
            destination_region1_obj, created = Region.objects.get_or_create(name=destination_region1, depth=1, province=destination_province_obj)

            # 2. update Request
            request.destination_province = destination_province_obj
            request.destination_region1 = destination_region1_obj
            update_fields.append('destination_province')
            update_fields.append('destination_region1')

            # 3. region2 needs null check
            if destination_region2:
                destination_region2_obj, created = Region.objects.get_or_create(name=destination_region2, depth=2, province=destination_province_obj, parent=destination_region1_obj)
                request.destination_region2 = destination_region2_obj
                update_fields.append('destination_region2')

            # update db 
            request.save(update_fields=update_fields, ignore_updated_at=True)


class NormalizeRequestTask(Task):
    def run(self, *args, **kwargs):
        # determine target requests
        max_normalized_id = RequestNormalized.objects.all().aggregate(Max('id'))
        most_recently_normalized = RequestNormalized.objects.get(id=max_normalized_id['id__max'])

        print 'Normalized until request {0}'.format(most_recently_normalized.ref_id)

        target_requests = Request.objects.filter(id__gt=most_recently_normalized.ref_id).order_by('created_at')

        if len(target_requests) == 0:
            print 'No target requests'
            return

        print 'New target request count: {0}'.format(len(target_requests))

        for request in target_requests:
            # normalize
            RequestNormalized.normalize(request)


# helper
def _sync_model_with_db(model_class, **kwargs): 
    obj, created = model_class.objects.get_or_create(**kwargs)
