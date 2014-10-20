from django.core.management.base import BaseCommand

from cabbie.apps.drive.bot.factory import PassengerBotFactory, DriverBotFactory


class Command(BaseCommand):
    help = 'Create passenger or driver bots'
    args = '<target> <count>'

    def handle(self, *args, **options):
        target = args[0]
        count = int(args[1])

        factory = (PassengerBotFactory() if target == 'passenger' else
                   DriverBotFactory() if target == 'driver' else
                   None)

        if factory is None:
            raise Exception('target should be one of `passenger` or `driver`')

        factory.create(count)
