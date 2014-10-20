from django.core.management.base import BaseCommand

from cabbie.apps.drive.bot.runner import PassengerBotRunner, DriverBotRunner


class Command(BaseCommand):
    help = 'Run passenger or driver bots'
    args = '<target> <count>'

    def handle(self, *args, **options):
        target = args[0]
        count = int(args[1])

        runner = (PassengerBotRunner() if target == 'passenger' else
                  DriverBotRunner() if target == 'driver' else
                  None)

        if runner is None:
            raise Exception('target should be one of `passenger` or `driver`')

        runner.run(count)
