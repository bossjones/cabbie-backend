import json,httplib

from django.conf import settings

from cabbie.apps.account.models import Driver
from cabbie.utils.log import LoggableMixin
from cabbie.utils.meta import SingletonMixin

class DriverLocationManager(LoggableMixin, SingletonMixin):
    ids = {}

    def get(self, driver_id):
        return self.ids.get(str(driver_id))

    def update(self, driver_id, object_id):
        self.ids[str(driver_id)] = object_id

    def remove(self, driver_id):
        self.ids.pop(str(driver_id))

    def recover(self):
        drivers = Driver.objects.filter(is_freezed=False)
        for driver in drivers:
            if driver.parse_location_object_id:
                self.update(driver.id, driver.parse_location_object_id)

    def deactivate(self, driver_id): 
        connection = httplib.HTTPSConnection(settings.PARSE_API_URL, settings.PARSE_HTTPS_PORT)
        connection.connect()
        object_id = self.get(driver_id)

        method = 'PUT'
        url = '/1/classes/{0}/{1}'.format(settings.PARSE_DRIVER_LOCATION_OBJECT, object_id)
    
        connection.request(method, url, json.dumps({
                    "activated": False,
                }), {
                "X-Parse-Application-Id": settings.PARSE_APPLICATION_ID,
                "X-Parse-REST-API-Key": settings.PARSE_REST_API_KEY,
                "Content-Type": "application/json"
            }
        )
        result = json.loads(connection.getresponse().read())

    def remove(self, object_id): 
        connection = httplib.HTTPSConnection(settings.PARSE_API_URL, settings.PARSE_HTTPS_PORT)
        connection.connect()

        method = 'DELETE'
        url = '/1/classes/{0}/{1}'.format(settings.PARSE_DRIVER_LOCATION_OBJECT, object_id)
    
        connection.request(method, url, '', {
                "X-Parse-Application-Id": settings.PARSE_APPLICATION_ID,
                "X-Parse-REST-API-Key": settings.PARSE_REST_API_KEY,
            }
        )
        result = json.loads(connection.getresponse().read())
        self.remove(driver_id)

     
    def update_location(self, driver_id, location):
        connection = httplib.HTTPSConnection(settings.PARSE_API_URL, settings.PARSE_HTTPS_PORT)
        connection.connect()
        
        object_id = self.get(driver_id)
            
        if object_id:   # update 
            method = 'PUT'
            url = '/1/classes/{0}/{1}'.format(settings.PARSE_DRIVER_LOCATION_OBJECT, object_id)
        
            connection.request(method, url, json.dumps({
                    "activated": True,
                    "location": {
                        "__type": "GeoPoint",
                        "latitude": location[1],
                        "longitude": location[0]
                    }
                }), {
                    "X-Parse-Application-Id": settings.PARSE_APPLICATION_ID,
                    "X-Parse-REST-API-Key": settings.PARSE_REST_API_KEY,
                    "Content-Type": "application/json"
                }
            )
            result = json.loads(connection.getresponse().read())

        else:           # create
            method = 'POST'
            url = '/1/classes/{0}'.format(settings.PARSE_DRIVER_LOCATION_OBJECT)
        
            connection.request(method, url, json.dumps({
                    "driver": driver_id, 
                    "activated": True,
                    "location": {
                        "__type": "GeoPoint",
                        "latitude": location[1],
                        "longitude": location[0]
                    }
                }), {
                    "X-Parse-Application-Id": settings.PARSE_APPLICATION_ID,
                    "X-Parse-REST-API-Key": settings.PARSE_REST_API_KEY,
                    "Content-Type": "application/json"
                }
            )
            result = json.loads(connection.getresponse().read())
            object_id = result['objectId']
            self.update(driver_id, object_id) 

            # make persistent
            try:
                driver = Driver.objects.get(pk=driver_id)
            except Driver.DoesNotExists, e:
                pass
            else:
                driver.parse_location_object_id = object_id
                driver.save(update_fields=['parse_location_object_id'])


