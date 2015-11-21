# scripts/request_normalize.py

import datetime

from django.conf import settings
from django.db.models import Max


from cabbie.apps.drive.models import Request, RequestNormalized

def run():
    # determine target requests
    max_normalized_id = RequestNormalized.objects.all().aggregate(Max('id'))
    most_recently_normalized = RequestNormalized.objects.get(id=max_normalized_id['id__max'])

    print 'Normalized until request {0}'.format(most_recently_normalized.ref_id)

    target_requests = Request.objects.filter(id__gt=most_recently_normalized.ref_id).order_by('created_at')

    if len(target_requests) == 0:
        print 'No target requests'
        return

    print 'New target request count: {0}'.format(len(target_requests))

    for request in target_requests:
        # normalize
        RequestNormalized.normalize(request)
