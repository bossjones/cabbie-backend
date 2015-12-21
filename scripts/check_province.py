# encoding: utf-8
# scripts/check_province.py

from cabbie.apps.account.models import Driver
from cabbie.apps.drive.models import Province, Region

def run():
    # check province
    drivers = Driver.objects.all()

    errors = []

    for driver in drivers:
        province = driver.province
        region = driver.region

        try:
            province_object = Province.objects.get(name=province)
        except Province.DoesNotExist, e:
            msg = u'{0} {1} {2} error province:{3}'.format(driver.id, driver.name, driver.phone, province)
            print msg
            errors.append(msg)
        else:    
            if region:
                try:
                    Region.objects.get(name=region, depth=1, province=province_object) 
                except Region.DoesNotExist, e:
                    msg = u'{0} {1} {2} error region:{3}'.format(driver.id, driver.name, driver.phone, region)
                    print msg
                    errors.append(msg)
