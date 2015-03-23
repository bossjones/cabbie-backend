# scripts/provide_signup_point.py

from django.conf import settings

from cabbie.apps.account.models import Passenger 
from cabbie.apps.payment.models import Transaction 

def run():
    for passenger in Passenger.objects.all():
        transaction_type = Transaction.SIGNUP_POINT

        # check if already awarded
        points = Transaction.objects.filter(user=passenger, transaction_type=transaction_type, state=Transaction.DONE)
        if len(points) > 0:
            print '{p} already proveded signup point, ignore'.format(p=passenger)
            continue

        amount = settings.POINTS_BY_TYPE.get(transaction_type)
        if amount:
            Transaction.objects.create(
                user=passenger,
                transaction_type=transaction_type,
                amount=amount,
                state=Transaction.DONE,
                note=Transaction.get_transaction_type_text(transaction_type)
            )
            print '{p} proveded new signup point'.format(p=passenger)
