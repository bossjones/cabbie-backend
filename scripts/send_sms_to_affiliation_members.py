# scripts/send_sms_to_affiliation_members.py

from cabbie.apps.account.models import Passenger
from cabbie.apps.affiliation.models import Affiliation 
from django.db.models import Q
from cabbie.utils.sms import send_sms

def run():

#    TEST
#    send_sms('sms/driver_event_20151123.txt', '01089861391', {})


    count = 0

    for affiliation in Affiliation.objects.all():

        members = affiliation.passengers.all() 

        count += len(members)

        for member in members:
            print 'Member {0}, {1}'.format(member.name, member.phone)

            # send
            send_sms('sms/affiliation_notice.txt', member.phone, {})

    print 'Total: {0}'.format(count)

