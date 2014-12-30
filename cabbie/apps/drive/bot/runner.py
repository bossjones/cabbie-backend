import random

from django.conf import settings

from cabbie.apps.account.models import Passenger, Driver
from cabbie.apps.drive.bot.driver import DriverBot
from cabbie.apps.drive.bot.passenger import PassengerBot
from cabbie.utils.ioloop import start
from cabbie.utils.log import LoggableMixin
from cabbie.utils.meta import SingletonMixin
from cabbie.utils.rand import Dice, random_float, random_int


class BotRunner(LoggableMixin, SingletonMixin):
    pass


class PassengerBotRunner(BotRunner):
    def run(self, count=1):
        self.info('Running {0} passenger bot(s)'.format(count))

        qs = Passenger.objects.select_related('auth_token')
        qs = qs.filter(is_bot=True).order_by('?')[:count]

        for passenger in qs:
            bot = PassengerBot(passenger)
            bot.start()

        start()


class DriverBotRunner(BotRunner):
    def run(self, count=1):
        self.info('Running {0} driver bot(s)'.format(count))

        qs = Driver.objects.select_related('auth_token')
        qs = qs.filter(is_bot=True).order_by('?')[:count]

        for driver in qs:
            start_location = [
                random_float(*settings.BOT_LONGITUDE_RANGE),
                random_float(*settings.BOT_LATITUDE_RANGE),
            ]
            speed = random_int(100, 300)
            reject_dice = Dice(
                (True, 1),
                (False, random_int(1, 10)),
            )
            charge_type_change_dice = Dice(
                (True, 1),
                (False, random_int(120, 300)),
            )
            direction_change_dice = Dice(
                (True, 1),
                (False, random_int(30, 300)),
            )

            bot = DriverBot(driver, start_location, speed, reject_dice,
                            charge_type_change_dice, direction_change_dice)
            bot.start()

        start()
