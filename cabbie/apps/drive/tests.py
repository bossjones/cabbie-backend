from django.test import TestCase
from django.conf import settings
from django.contrib.gis.geos import Point

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from cabbie.apps.drive.models import Ride
from cabbie.apps.account.models import Passenger, Driver

class InternalRideAPITests(APITestCase):
    def setUp(self):
        # prepare data
        self.driver = self._create_driver()
        self.passenger = self._create_passenger()        

                
        # create two rides
        self.ride1 = self._create_ride() 
        self.ride2 = self._create_ride() 
       
    def _authenticate(self):
        token = Token.objects.get(user=self.passenger)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    def _create_driver(self):
        # make driver
        return Driver.objects.create(
            phone='01012340000',
            name='Driver Kim', 
        )
    
    def _create_passenger(self):
        # make passenger
        return Passenger.objects.create(
            phone='01012340001',
            name='Passenger Kim', 
        )
    
    def _create_ride(self):
        source = {'location': [126.9851593, 37.5663155]}
        destination = {'location': [126.9831594, 37.5703983]}

        data = {
            'passenger_id': self.passenger.id,
            'driver_id': self.driver.id,
            'source': source,
            'destination': destination,
            'state': Ride.REQUESTED,
            'charge_type': 1000,
            'passenger_location': source.get('location'),
            'driver_location': source.get('location'),
        }

        return Ride.objects.create(
            passenger_id=data['passenger_id'],
            driver_id=data['driver_id'],
            state=data['state'],
            source=source,
            source_location=Point(*source['location']),
            destination=destination,
            destination_location=Point(*destination['location']),
            charge_type=data['charge_type']
        )

 
    def _update_rating(self, ride_id, **kwargs):
        url = '/api/rides/{0}/rate'.format(ride_id)
    
        data = { 'ratings_by_category': kwargs, 'comment': '' }

        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)  

    def _get_driver_rating(self):
        url = '/api/drivers/{0}'.format(self.driver.id)
        response = self.client.get(url, format='json')
        return response.data['rating']

    def test_internal_ride_create(self):
        """
        Ensure that we can create a new ride object
        """
        
        self._authenticate()
        
        # update first to ride1
        kindness = 5
        cleanliness = 4
        security = 4

        total1 = float(kindness + cleanliness + security)

        self._update_rating(self.ride1.id, kindness=kindness, cleanliness=cleanliness, security=security)
        self.assertEqual(self._get_driver_rating(), total1 / 3) 
                
        # update first to ride2
        kindness = 1
        cleanliness = 2
        security = 3
        
        total2 = total1 + float(kindness + cleanliness + security)

        self._update_rating(self.ride2.id, kindness=kindness, cleanliness=cleanliness, security=security)
        self.assertEqual(self._get_driver_rating(), total2 / 6) 
        
        # update second to ride2
        kindness = 3
        cleanliness = 4
        security = 4
        
        total3 = total1 + float(kindness + cleanliness + security)

        self._update_rating(self.ride2.id, kindness=kindness, cleanliness=cleanliness, security=security)
        self.assertEqual(self._get_driver_rating(), total3 / 6) 

        # update second to ride1 with one more category
        kindness = 3
        cleanliness = 4
        security = 3
        convenience = 5
        
        total4 = total3 - total1 + float(kindness + cleanliness + security + convenience)

        self._update_rating(self.ride1.id, kindness=kindness, cleanliness=cleanliness, security=security, convenience=convenience)
        self.assertEqual(self._get_driver_rating(), total4 / 7) 

