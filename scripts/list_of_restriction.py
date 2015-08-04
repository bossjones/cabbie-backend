# scripts/list_of_restriction.py

from django.conf import settings

from cabbie.apps.account.models import Driver 
from cabbie.apps.drive.models import Ride

def run():
    for driver in Driver.objects.filter(is_freezed=False):
        rides = driver.rides.filter(state=Ride.RATED)

        rates = [ride.rating * 3 for ride in rides]

        if len(rates) >= 3:
            avg = sum(rates) / float(len(rates))

            if avg < 4.0:
                print '{name},{phone},{rating_count},{rating:.0f}'.format(
                    name=driver.name, phone=driver.phone,
                    rating_count=len(rates), rating=avg)

