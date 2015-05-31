import datetime

from django.db import models
from django.utils import timezone

from cabbie.apps.drive.models import Ride
from cabbie.utils.date import week_of_month

class DriverRideStatManager(models.Manager):
    def normalize(self, value):
        if value and isinstance(value, datetime.datetime) and value.tzinfo:
            return timezone.get_current_timezone().normalize(value)
        else:
            return value

class DriverRideStatMonthManager(DriverRideStatManager):
    def sync(self, ride_history):
        if not ride_history.driver:
            return

        # normalize
        date = self.normalize(ride_history.ride.created_at).date()

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
        
        # normalize
        date = self.normalize(ride.created_at).date()

        stat_boarded, created = self.get_or_create(driver=ride.driver, year=date.year, month=date.month,
            state=Ride.BOARDED)
        stat_completed, created = self.get_or_create(driver=ride.driver, year=date.year, month=date.month,
            state=Ride.COMPLETED)
        stat_rated, created = self.get_or_create(driver=ride.driver, year=date.year, month=date.month,
            state=Ride.RATED)

        # ratings
        stat_boarded.ratings[u'{id}'.format(id=ride.id)] = ride.ratings_by_category
        stat_completed.ratings[u'{id}'.format(id=ride.id)] = ride.ratings_by_category
        stat_rated.ratings[u'{id}'.format(id=ride.id)] = ride.ratings_by_category
        
        # rides
        if ride.id in stat_boarded.rides: pass
        else: stat_boarded.rides.append(ride.id)

        if ride.id in stat_completed.rides: pass
        else: stat_completed.rides.append(ride.id)

        if ride.id in stat_rated.rides: pass
        else: stat_rated.rides.append(ride.id)

        stat_boarded.save(update_fields=['rides', 'ratings'])
        stat_completed.save(update_fields=['rides', 'ratings'])
        stat_rated.save(update_fields=['rides', 'ratings'])

        # update rating in driver account, only done from month stat
        ride.driver._update_rating()

    def sync_delete(self, ride_history):
        if not ride_history.driver:
            return

        # normalize
        date = self.normalize(ride_history.ride.created_at).date()

        stat, created = self.get_or_create(
            driver=ride_history.driver, year=date.year, month=date.month,
            state=ride_history.state)

        # rides
        if ride_history.ride.id in stat.rides:
            pass
        else:
            stat.rides.append(ride_history.ride.id)
        
        stat.save(update_fields=['rides'])
    

class DriverRideStatWeekManager(DriverRideStatManager):
    def sync(self, ride_history):
        if not ride_history.driver:
            return

        # normalize
        date = self.normalize(ride_history.ride.created_at).date()

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
        
        # normalize
        date = self.normalize(ride.created_at).date()
        week = week_of_month(date)

        stat_boarded, created = self.get_or_create(driver=ride.driver, year=date.year, month=date.month, week=week,
            state=Ride.BOARDED)
        stat_completed, created = self.get_or_create(driver=ride.driver, year=date.year, month=date.month, week=week,
            state=Ride.COMPLETED)
        stat_rated, created = self.get_or_create(driver=ride.driver, year=date.year, month=date.month, week=week,
            state=Ride.RATED)

        # ratings
        stat_boarded.ratings[u'{id}'.format(id=ride.id)] = ride.ratings_by_category
        stat_completed.ratings[u'{id}'.format(id=ride.id)] = ride.ratings_by_category
        stat_rated.ratings[u'{id}'.format(id=ride.id)] = ride.ratings_by_category
        
        # rides
        if ride.id in stat_boarded.rides: pass
        else: stat_boarded.rides.append(ride.id)

        if ride.id in stat_completed.rides: pass
        else: stat_completed.rides.append(ride.id)

        if ride.id in stat_rated.rides: pass
        else: stat_rated.rides.append(ride.id)

        stat_boarded.save(update_fields=['rides', 'ratings'])
        stat_completed.save(update_fields=['rides', 'ratings'])
        stat_rated.save(update_fields=['rides', 'ratings'])


class DriverRideStatDayManager(DriverRideStatManager):
    def sync(self, ride_history):
        if not ride_history.driver:
            return

        # normalize
        date = self.normalize(ride_history.ride.created_at).date()
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
        
        # normalize
        date = self.normalize(ride.created_at).date()
        week = week_of_month(date)

        stat_boarded, created = self.get_or_create(driver=ride.driver, year=date.year, month=date.month, week=week, day=date.day,
            state=Ride.BOARDED)
        stat_completed, created = self.get_or_create(driver=ride.driver, year=date.year, month=date.month, week=week, day=date.day,
            state=Ride.COMPLETED)
        stat_rated, created = self.get_or_create(driver=ride.driver, year=date.year, month=date.month, week=week, day=date.day,
            state=Ride.RATED)

        # ratings
        stat_boarded.ratings[u'{id}'.format(id=ride.id)] = ride.ratings_by_category
        stat_completed.ratings[u'{id}'.format(id=ride.id)] = ride.ratings_by_category
        stat_rated.ratings[u'{id}'.format(id=ride.id)] = ride.ratings_by_category
        
        # rides
        if ride.id in stat_boarded.rides: pass
        else: stat_boarded.rides.append(ride.id)

        if ride.id in stat_completed.rides: pass
        else: stat_completed.rides.append(ride.id)

        if ride.id in stat_rated.rides: pass
        else: stat_rated.rides.append(ride.id)

        stat_boarded.save(update_fields=['rides', 'ratings'])
        stat_completed.save(update_fields=['rides', 'ratings'])
        stat_rated.save(update_fields=['rides', 'ratings'])
