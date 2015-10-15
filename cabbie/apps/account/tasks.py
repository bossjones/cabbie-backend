from celery.task import Task
from django.conf import settings
from django.utils import timezone

from cabbie.apps.account.models import Driver, DriverLocation

from cabbie.utils.parse import ParseManager

class ActiveDriverHourlyTask(Task):
    def run(self, *args, **kwargs):
        limit = 100
        loop = 0

        fetched = 0

        while True:
            locations = ParseManager()._get(settings.PARSE_OBJECT_DRIVER_LOCATION, limit=limit, skip=loop*limit) 
            results = locations['results']

            if results: 
                fetched += len(results)
                
                for driver_location in results:
                    # sync with db
                    DriverLocation.update(driver_location)

                loop += 1
            else:
                break;


class DormantDriverDailyTask(Task):
    def run(self, *args, **kwargs):
        now = timezone.now()
        for driver in Driver.objects.filter(is_accepted=True,
                                            is_freezed=False):
            days = (now - driver.last_active_at).days
            is_dormant = days > settings.DORMANT_DRIVER_DAYS
            if is_dormant != driver.is_dormant:
                driver.is_dormant = is_dormant
                driver.save(update_fields=['is_dormant'])


class SuperDriverMonthlyTask(Task):
    def run(self, *args, **kwargs):
        for driver in Driver.objects.filter(is_accepted=True,
                                            is_freezed=False):
            # Rollover
            driver.previous_month_board_count = \
                driver.current_month_board_count
            driver.current_month_board_count = 0
            driver.is_super = (driver.previous_month_board_count
                               >= settings.SUPER_DRIVER_THRESHOLD)
            driver.save(update_fields=[
                'previous_month_board_count', 'current_month_board_count',
                'is_super'])
