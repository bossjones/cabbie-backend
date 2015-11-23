# scripts/send_sms_to_drivers.py

from cabbie.apps.account.models import Driver
from cabbie.apps.drive.models import Ride
from django.db.models import Q
from cabbie.utils.sms import send_sms

def run():

#    TEST
#    send_sms('sms/driver_event_20151123.txt', '01089861391', {})

    i = 0

    for driver in Driver.objects.filter(is_freezed=False):

        ride_count = Ride.objects.filter(driver=driver).filter(Q(state=Ride.BOARDED) | Q(state=Ride.COMPLETED) | Q(state=Ride.RATED)).count()

        if ride_count == 0:
            i += 1
            # send
        #    send_sms('sms/driver_event_20151123.txt', driver.phone, {})
            print '{0} {1}'.format(i, driver.name)

    print 'Total: {0}'.format(i)

