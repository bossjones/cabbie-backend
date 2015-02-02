# scripts/reset_driver_rating.py

from cabbie.apps.account.models import Driver

def run():
    for driver in Driver.objects.all():
        driver._update_rating()


