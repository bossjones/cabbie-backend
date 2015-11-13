# scripts/data_extraction.py

from cabbie.apps.drive.models import Request

def run():
    for month in [3,4,5,6,7,8,9,10,11]:
        requests = Request.objects.exclude(contacts=None).filter(created_at__month=month)

        ids = set()

        for req in requests:
            ids.update(req.contacts)
            ids.update(req.rejects)
        
            if req.approval and req.approval.driver:
                ids.add(req.approval.driver.id)

        print 'month:{0}, active:{1}'.format(month, len(ids))

            
        






