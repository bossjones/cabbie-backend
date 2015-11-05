# scripts/request_normalize.py

from cabbie.apps.drive.models import Request, RequestNormalized

def run():
    # cleanup normalized table
    RequestNormalized.objects.all().delete()

    # normalize
    for request in Request.objects.order_by('created_at'):
        RequestNormalized.normalize(request)
