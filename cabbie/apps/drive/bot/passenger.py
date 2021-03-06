# encoding: utf-8

import random
import requests
from urlparse import urljoin

from django.conf import settings
from rest_framework.authtoken.models import Token

from cabbie.apps.drive.bot.base import Bot
from cabbie.utils.ioloop import delay
from cabbie.utils.geo import move, distance
from cabbie.utils.rand import random_float
from cabbie.utils import json


class PassengerBot(Bot):
    # States
    (
        INITIALIZED,
        REQUESTED,
        APPROVED,
        ARRIVED,
        BOARDED,
    ) = range(5)

    role = 'passenger'
    request_delay = 1
    rewatch_delay = 5
    additional_message_types = ['kid', 'pregnant', 'luggage', 'emergency']
    place_choices = [
        ('르메이에르 종로타운', '서울시 종로구 종로1가 24'),
        ('선릉역 8번출구', '서울시 강남구 역삼동'),
        ('강남역 지오다노', '서울시 강남구 역삼동 821-1'),
        ('서울역', '서울시 용산구 청파로 378')
    ]

    web_base_url = 'http://{0}:{1}'.format(settings.WEB_SERVER_HOST, settings.WEB_SERVER_PORT)

    def __init__(self, instance):
        super(PassengerBot, self).__init__(instance)
        self._pickup_location = None 

        self._state = None
        self._source = None
        self._destination = None

        self._candidates = None
        self._best = None

        self._charge_type = 1000 

    # Handlers
    # --------

    def handle_auth_succeeded(self):
        self.info('Auth succeded')

        self._state = self.INITIALIZED

        self._watch()

    def handle_passenger_assigned(self, assignment):

        self._candidates = assignment['candidates'] if assignment else None

        if self._candidates and len(self._candidates) > 0:

            self._best = assignment['best']
            
            self.info('Assigned {0} drivers'.format(len(self._candidates)))

            delay(self.request_delay, self._request)
            
            return
       
        self.info('Assigned nothing') 
        self.candidates = None


    def handle_passenger_approved(self):
        self.info('Approved')

        self._state = self.APPROVED

    def handle_passenger_rejected(self, reason):
        self.info('Rejected')

        self._state = self.INITIALIZED

        delay(self.rewatch_delay, self._watch)

    def handle_passenger_arrived(self):
        self.info('Arrived')

        self._state = self.ARRIVED

    def handle_passenger_boarded(self, ride_id):
        self.info('Boarded')

        self._state = self.BOARDED

    def handle_passenger_progress(self, location, estimate):
        self.info('Updating driver progress {0}m remains'.format(distance(location, self._source['location'])))

    def handle_passenger_journey(self, location, journey):
        self.info('Updating driver journey {0}m remains'.format(distance(location, self._destination['location'])))

    def handle_passenger_completed(self, ride_id, summary):
        self.info('Completed ride {0}'.format(ride_id))

        self._state = self.INITIALIZED

        # update rating
        rate_url = '/api/rides/{0}/rate'.format(ride_id)
        url = urljoin(self.web_base_url, rate_url)

        payload = {
            'ratings_by_category': json.dumps({
                'kindness': random.randint(0, 5),
                'cleanliness': random.randint(0, 5),
                'security': random.randint(0, 5),
            }),
            'comment': '',
        }

        token = Token.objects.get(user=self._instance)
        headers = {
            'Authorization': 'Token {0}'.format(token),
        }

        try:
            r = requests.put(url, data=payload, headers=headers)
        except Exception as e:
            self.error('Failed to rate: {0}'.format(e))

        # rewatch
        delay(self.rewatch_delay, self._watch)

    def handle_passenger_disconnected(self):
        self.info('Disconnected')

        self._state = self.INITIALIZED

    # Pubsub
    # ------


    # Actions
    # -------
    def _watch(self):
        self.info('Watching')
        
        pickup_location = [
            random_float(*settings.BOT_LONGITUDE_RANGE),
            random_float(*settings.BOT_LATITUDE_RANGE),
        ]
        self._source = {}
        self._source['location'] = pickup_location
        poi, address = random.choice(self.place_choices)
        self._source['poi'] = poi 
        self._source['address'] = address

        self.send('passenger_watch', {
            'location': self._source['location'],
            'charge_type': self._charge_type,
        })

    def _unwatch(self):
        self.info('Unwatching')
        self.send('passenger_unwatch')

    def _request(self):
        if self._state == self.REQUESTED: return

        self.info('Requesting')

        self._state = self.REQUESTED
        
        destination_location= [
            random_float(*settings.BOT_LONGITUDE_RANGE),
            random_float(*settings.BOT_LATITUDE_RANGE),
        ]
        self._destination = {}
        self._destination['location'] = destination_location
        poi, address = random.choice(self.place_choices)
        self._destination['poi'] = poi
        self._destination['address'] = address

        data = {
            'driver_id': self._select_driver(), 
            'charge_type': self._charge_type,
            'source': self._source,
            'destination': self._destination,
            'additional_message': { 'types': self._random_additional_message(), 'comment': '' }
        }

        self.send('passenger_request', data)

    def _cancel(self):
        self.info('Canceling')
        self.send('passenger_cancel')


    def _select_driver(self):
        return random.choice(self._candidates)['driver']['id']


    def _random_additional_message(self):
        _list = self.additional_message_types
        random.shuffle(_list)
      
        pick = random.randint(0, len(_list)) 
        
        return [_list[i] for i in range(pick)]
        
        
