from cabbie.apps.drive.models import SecureNumber
from cabbie.apps.drive.bot.factory import BotFactory

generate_count = 100 


def run():
    secure_numbers = SecureNumber.objects.all() 

    if len(secure_numbers) > 0:
        print 'Secure numbers exist already'

    for i in range(generate_count):
        phone = '0506{0}'.format(BotFactory.random_zfill_int(8))
        state = SecureNumber.RELEASED

        SecureNumber(phone=phone, state=state).save()
        print '{0} is created'.format(phone)

