from cabbie.apps.account.models import Driver

def run():
    drivers = Driver.objects.all()
    for driver in drivers:
        driver.car_number = driver.car_number.replace(u' ', u'')
        driver.save(update_fields=['car_number'])
