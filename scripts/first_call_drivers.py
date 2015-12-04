# scripts/first_call_drivers.py

import datetime
from django.db.models import Q

from cabbie.apps.drive.models import Ride
from cabbie.apps.account.models import Driver

def run():
    start_time = datetime.datetime.strptime('2015-11-23', "%Y-%m-%d")
    end_time = datetime.datetime.strptime('2015-11-30', "%Y-%m-%d")

    rides = Ride.objects.filter(created_at__gte=start_time, created_at__lt=end_time).filter(Q(state=Ride.BOARDED) | Q(state=Ride.COMPLETED) | Q(state=Ride.RATED))

    drivers = Driver.objects.all()
    
    for ride in rides:
        if ride.driver:
            first_ride = ride.driver.rides.filter(Q(state=Ride.BOARDED) | Q(state=Ride.COMPLETED) | Q(state=Ride.RATED)).order_by('id')[0] # not crash
            if ride.id == first_ride.id:
                print u'{drive_ride},{driver_name},{driver_phone}'.format(drive_ride=ride.id, driver_name=ride.driver.name, driver_phone=ride.driver.phone)
