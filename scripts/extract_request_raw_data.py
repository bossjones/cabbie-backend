# scripts/extract_request_raw_data.py

import datetime

from django.conf import settings
from cabbie.apps.drive.models import Request

def run():
    launch_date = datetime.datetime.strptime(settings.BKTAXI_GRAND_LAUNCH_DATE, "%Y-%m-%d").date()
    FORMAT = u'{req_id}&{req_created_at}&{psg_name}&{src_poi}&{src_addr}&{dest_poi}&{dest_addr}&{distance}&{req_state}&{ride_id}&{driver_name}&{ride_created_at}&{ride_state}&{rate_kind}&{rate_clean}&{rate_secure}&{rate_comment}'

    with open('raw_data.csv', 'w') as f:

        for request in Request.objects.filter(created_at__gte=launch_date).order_by('-created_at'): 
            data = {}
            data['req_id'] = request.id 
            data['req_created_at'] = request.created_at
            data['psg_name'] = request.passenger.name if request.passenger else ''
            data['src_poi'] = request.source['poi'] if request.source else ''
            data['src_addr'] = request.source['address'] if request.source else ''
            data['dest_poi'] = request.destination['poi'] if request.destination else ''
            data['dest_addr'] = request.destination['address'] if request.destination else ''
            data['distance'] = request.distance
            data['req_state'] = request.state
            data['ride_id'] = request.approval.id if request.approval else ''
            data['driver_name'] = request.approval.driver.name if request.approval and request.approval.driver else '' 
            data['ride_created_at'] = request.approval.created_at if request.approval else ''
            data['ride_state'] = request.approval.state if request.approval else '' 
            data['rate_kind'] = request.approval.ratings_by_category['kindness'] if request.approval and request.approval.ratings_by_category else ''
            data['rate_clean'] = request.approval.ratings_by_category['cleanliness'] if request.approval and request.approval.ratings_by_category else ''
            data['rate_secure'] = request.approval.ratings_by_category['security'] if request.approval and request.approval.ratings_by_category else '' 
            data['rate_comment'] = request.approval.comment if request.approval else '' 

            result = FORMAT.format(**data)

            print result
            f.write(result + '\n')
