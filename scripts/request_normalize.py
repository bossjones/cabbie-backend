# scripts/request_normalize.py

import datetime

from django.conf import settings

from cabbie.apps.drive.models import Request, RequestNormalized

def run():
    # cleanup normalized table
    RequestNormalized.objects.all().delete()

    launch_date = datetime.datetime.strptime(settings.BKTAXI_GRAND_LAUNCH_DATE, "%Y-%m-%d").date()

    # normalize
    for request in Request.objects.filter(created_at__gte=launch_date).order_by('created_at'):
        RequestNormalized.normalize(request)
