from django.db import models

from cabbie.apps.drive.models import Ride
from cabbie.utils.date import week_of_month


class DriverRideStatMonthManager(models.Manager):
    def sync_count(self, ride_history):
        if not ride_history.driver:
            return

        if ride_history.state not in (Ride.REJECTED, Ride.CANCELED,
                                      Ride.BOARDED):
            return

        date = ride_history.ride.created_at_future.date()
        stat, created = self.get_or_create(
            driver=ride_history.driver, year=date.year, month=date.month,
            state=ride_history.state)
        stat.count += 1
        stat.save(update_fields=['count'])
    
    def sync_rate(self, ride):
        if not ride:
            return
        
        date = ride.created_at_future.date()
        stat, created = self.get_or_create(
            driver=ride.driver, year=date.year, month=date.month,
            state=Ride.BOARDED)

        stat.ratings[u'{id}'.format(id=ride.id)] = ride.ratings_by_category
        stat.save(update_fields=['ratings'])

class DriverRideStatWeekManager(models.Manager):
    def sync_count(self, ride_history):
        if not ride_history.driver:
            return

        if ride_history.state not in (Ride.REJECTED, Ride.CANCELED,
                                      Ride.BOARDED):
            return

        date = ride_history.ride.created_at_future.date()
        week = week_of_month(date)
        stat, created = self.get_or_create(
            driver=ride_history.driver, year=date.year, month=date.month,
            week=week, state=ride_history.state)
        stat.count += 1
        stat.save(update_fields=['count'])
    
    def sync_rate(self, ride):
        if not ride:
            return
        
        date = ride.created_at_future.date()
        week = week_of_month(date)
        stat, created = self.get_or_create(
            driver=ride.driver, year=date.year, month=date.month,
            week=week, state=Ride.BOARDED)

        stat.ratings[u'{id}'.format(id=ride.id)] = ride.ratings_by_category
        stat.save(update_fields=['ratings'])

class DriverRideStatDayManager(models.Manager):
    def sync_count(self, ride_history):
        if not ride_history.driver:
            return

        if ride_history.state not in (Ride.REJECTED, Ride.CANCELED,
                                      Ride.BOARDED):
            return

        date = ride_history.ride.created_at_future.date()
        week = week_of_month(date)
        stat, created = self.get_or_create(
            driver=ride_history.driver, year=date.year, month=date.month,
            week=week, day=date.day, state=ride_history.state)
        stat.count += 1
        stat.save(update_fields=['count'])
    
    def sync_rate(self, ride):
        if not ride:
            return
        
        date = ride.created_at_future.date()
        week = week_of_month(date)
        stat, created = self.get_or_create(
            driver=ride.driver, year=date.year, month=date.month,
            week=week, day=date.day, state=Ride.BOARDED)

        stat.ratings[u'{id}'.format(id=ride.id)] = ride.ratings_by_category
        stat.save(update_fields=['ratings'])

