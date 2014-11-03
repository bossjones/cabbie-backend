from django.db import models

from cabbie.apps.drive.models import Ride
from cabbie.utils.date import week_of_month


class DriverRideStatManager(models.Manager):
    def sync(self, ride_history):
        if not ride_history.driver:
            return

        if ride_history.state not in (Ride.REJECTED, Ride.CANCELED,
                                      Ride.BOARDED):
            return

        date = ride_history.created_at.date()
        week = week_of_month(date)
        stat, created = self.get_or_create(
            driver=ride_history.driver, year=date.year, month=date.month,
            week=week, state=ride_history.state)
        stat.count += 1
        stat.save(update_fields=['count'])
