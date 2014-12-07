from django.test import TestCase
from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase

class AccountTests(APITestCase):
    def test_passenger_signup(self):
        """
        Ensure that we can create a new passenger object
        """
        url = reverse('api-passengers-signup')
        data = {
                'name' : 'John Lennon', 
                'phone' : '01012340000', 
                'password' : '0000', 
                'email' : 'kokookko1@gmail.com', 
                }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
