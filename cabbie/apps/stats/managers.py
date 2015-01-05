from django.db import models

from cabbie.apps.drive.models import Ride
from cabbie.utils.date import week_of_month


class DriverRideStatMonthManager(models.Manager):
    def sync(self, ride_history):
        if not ride_history.driver:
            return

        date = ride_history.ride.created_at.date()
        stat, created = self.get_or_create(
            driver=ride_history.driver, year=date.year, month=date.month,
            state=ride_history.state)

        # rides
        if ride_history.ride.id in stat.rides:
            pass
        else:
            stat.rides.append(ride_history.ride.id)
        
        stat.save(update_fields=['rides'])
    
    def sync_rate(self, ride):
        if not ride:
            return
        
        date = ride.created_at.date()
        stat, created = self.get_or_create(
            driver=ride.driver, year=date.year, month=date.month,
            state=Ride.RATED)

        # ratings
        stat.ratings[u'{id}'.format(id=ride.id)] = ride.ratings_by_category
        
        # rides
        if ride.id in stat.rides:
            pass
        else:
            stat.rides.append(ride.id)

        stat.save(update_fields=['rides', 'ratings'])

        # update rating in driver account, only done from month stat
        ride.driver._update_rating()

class DriverRideStatWeekManager(models.Manager):
    def sync(self, ride_history):
        if not ride_history.driver:
            return

        date = ride_history.ride.created_at.date()
        week = week_of_month(date)
        stat, created = self.get_or_create(
            driver=ride_history.driver, year=date.year, month=date.month,
            week=week, state=ride_history.state)

        # rides
        if ride_history.ride.id in stat.rides:
            pass
        else:
            stat.rides.append(ride_history.ride.id)

        stat.save(update_fields=['rides'])
    
    def sync_rate(self, ride):
        if not ride:
            return
        
        date = ride.created_at.date()
        week = week_of_month(date)
        stat, created = self.get_or_create(
            driver=ride.driver, year=date.year, month=date.month,
            week=week, state=Ride.RATED)
        
        # ratings
        stat.ratings[u'{id}'.format(id=ride.id)] = ride.ratings_by_category

        # rides
        if ride.id in stat.rides:
            pass
        else:
            stat.rides.append(ride.id)

        stat.save(update_fields=['rides', 'ratings'])

class DriverRideStatDayManager(models.Manager):
    def sync(self, ride_history):
        if not ride_history.driver:
            return

        date = ride_history.ride.created_at.date()
        week = week_of_month(date)
        stat, created = self.get_or_create(
            driver=ride_history.driver, year=date.year, month=date.month,
            week=week, day=date.day, state=ride_history.state)

        # rides
        if ride_history.ride.id in stat.rides:
            pass
        else:
            stat.rides.append(ride_history.ride.id)

        stat.save(update_fields=['rides'])
    
    def sync_rate(self, ride):
        if not ride:
            return
        
        date = ride.created_at.date()
        week = week_of_month(date)
        stat, created = self.get_or_create(
            driver=ride.driver, year=date.year, month=date.month,
            week=week, day=date.day, state=Ride.RATED)

        # ratings
        stat.ratings[u'{id}'.format(id=ride.id)] = ride.ratings_by_category

        # rides
        if ride.id in stat.rides:
            pass
        else:
            stat.rides.append(ride.id)

        stat.save(update_fields=['rides', 'ratings'])

