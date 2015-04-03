# encoding: utf-8

from cabbie.apps.account.models import Driver

def run():
    drivers = Driver.objects.all()
    for driver in drivers:
        region_flag = driver.car_number[:2]
        
        if region_flag in ['31', '32']:
            driver.province = u'서울'
            driver.save(update_fields=['province'])
