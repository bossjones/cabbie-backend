# scripts/normalized_rate.py

from cabbie.apps.drive.models import Request, RequestNormalized, Ride

def run():
    rns = RequestNormalized.objects.filter(created_at__gte='2015-10-15', parent=None)

    total = len(rns)
    completed = 0

#   for normalized in rns: 
#       if normalized.is_completed():
#           completed += 1

    print 'total:{0}, completed:{1}'.format(total, completed)
