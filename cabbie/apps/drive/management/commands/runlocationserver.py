from django.core.management.base import BaseCommand

from cabbie.apps.drive.server import LocationServer


class Command(BaseCommand):
    help = 'Run location server'

    def handle(self, *args, **options):
        LocationServer().start()
