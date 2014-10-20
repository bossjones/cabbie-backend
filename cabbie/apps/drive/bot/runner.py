from cabbie.apps.account.models import Passenger, Driver
from cabbie.apps.drive.bot.driver import DriverBot
from cabbie.utils.ioloop import start
from cabbie.utils.log import LoggableMixin
from cabbie.utils.meta import SingletonMixin


class BotRunner(LoggableMixin, SingletonMixin):
    def run(self, count=1):
        self.info('Running {0} bot(s)'.format(count))

        instance = Driver.objects.filter(is_bot=True).order_by('?')[0]
        DriverBot(instance).start()

        start()


class PassengerBotRunner(BotRunner):
    pass


class DriverBotRunner(BotRunner):
    pass
