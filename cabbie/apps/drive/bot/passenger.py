# encoding: utf-8

import random

from django.conf import settings

from cabbie.apps.drive.bot.base import Bot
from cabbie.utils.ioloop import delay
from cabbie.utils.rand import random_float


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
        if assignment:

            self._candidates = assignment['candidates']
            self._best = assignment['best']
            
            self.info('Assigned {0} drivers'.format(len(self._candidates)))

            delay(self.request_delay, self._request)
            
            return
       
        self.info('Assigned nothing') 


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

    def handle_passenger_boarded(self):
        self.info('Boarded')

        self._state = self.BOARDED

    def handle_passenger_progress(self, location, estimate):
        self.info('Updating driver progress')

    def handle_passenger_journey(self, location, journey):
        self.info('Updating driver journey')

    def handle_passenger_completed(self, ride_id, summary):
        self.info('Completed ride {0}'.format(ride_id))

        self._state = self.INITIALIZED

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

        data = {
            'driver_id': self._select_driver(), 
            'charge_type': self._charge_type,
            'source': self._source,
            'destination': self._destination,
        }

        print data
        self.send('passenger_request', data)

    def _cancel(self):
        self.info('Canceling')
        self.send('passenger_cancel')


    def _select_driver(self):
        return random.choice(self._candidates)['driver']['id']

