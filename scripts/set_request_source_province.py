# scripts/set_request_source_province.py 

from cabbie.apps.drive.models import Province, Request

def run():

    # list up province
    for request in Request.objects.filter(source_province=None):
        address = request.source['address'] 
        addresses = address.split()

        if len(addresses) >= 1:
            province_name = addresses[0]
            
            try:
                old_province = Province.objects.get(name=province_name)
            except Province.DoesNotExist, e:
                # add new province and update 
                new_province = Province(name=province_name)
                new_province.save()
                print '{0} has been updated...'.format(province_name) 

                request.source_province = new_province
            else:
                request.source_province = old_province
                
            request.save(update_fields=['source_province'])
