import time
from collections import defaultdict
from functools import partial

from django.conf import settings
from tornado import gen

from cabbie.apps.drive.models import Request
from cabbie.apps.drive.location.estimate import HaversineEstimator
from cabbie.apps.drive.location.geo import Location
from cabbie.apps.drive.location.model import ModelManager
from cabbie.apps.drive.location.secret import fetch, post
from cabbie.apps.drive.location.driver import DriverManager 
from cabbie.apps.drive.location.proxy import RideProxyManager 
from cabbie.utils.geo import distance, Rtree2D
from cabbie.utils.ioloop import delay, cancel
from cabbie.utils.log import LoggableMixin
from cabbie.utils.push import send_push_notification
from cabbie.utils.meta import SingletonMixin
from cabbie.utils.pubsub import PubsubMixin


class RequestProxyManager(LoggableMixin, SingletonMixin, PubsubMixin):
    """Manages ride call requests """

    def __init__(self):
        super(RequestProxyManager, self).__init__()

        self._requests = {}
        
    def create(self, passenger, source, destination, additional_message):
        self.info(u'Create request {passenger} with {source_location}'.format(passenger=passenger, source_location=source['location']))
        # create proxy
        proxy = RequestProxy(passenger, source, destination, additional_message)
        request_id = proxy.create()

        # register
        self._requests[str(request_id)] = proxy 
        print self._requests
        
        return proxy 
    
    def unregister(self, request_id):
        self.info(u'Unregister {passenger}'.format(passenger=passenger))
        # unregister
        self._requests.pop(str(passenger.id), None)
        
    def add_requestee(self, driver_id):
        self._requested_drivers[str(driver_id)]
         
    def is_requested(self, driver_id): 
        return str(driver_id) in self._requested_drivers

    def approve(self, request_id, driver_id):
        request = self._requests.get(str(request_id), None)

        if request is None:
            self.info('Request {0} gone, approval by {1} failed'.format(request_id, driver_id))
            return False, None

        # Fetch the last driver info before deactivating
        driver_location = DriverManager().get_driver_location(driver_id)
        driver_charge_type = DriverManager().get_driver_charge_type(driver_id)

        approved = request.approve(driver_id)

        if not approved:
            return False, None

        # Create a new ride proxy instance from information in approved request
        proxy = RideProxyManager().create(request._passenger.id, request._source, request._destination, request._additional_message)
        proxy.set_driver(driver_id, driver_location, driver_charge_type)

        # notify to driver
        proxy.request()
        proxy.approve()

        return True, proxy._ride_id
        
    def reject(self, request_id, driver_id):
        request = self._requests.get(str(request_id), None)

        if request is None:
            self.info('Request {0} gone, rejection by {1} failed'.format(request_id, driver_id))
            return False

        return request.reject(driver_id)
 

class RequestProxy(LoggableMixin, PubsubMixin):
    """ 
    Proxy of `Request` model for asynchronous save operation
    """
    
    create_path = '/_/drive/request/create'
    update_path = '/_/drive/request/{pk}/update'
    refresh_interval = settings.LOCATION_REFRESH_INTERVAL
    refresh_count = 10
    candidate_count = settings.CANDIDATE_COUNT
    reassign_count = settings.REASSIGN_COUNT
    max_distance = settings.MAX_DISTANCE
    charge_type = 1000
    approved = False

    def __init__(self, passenger, source, destination, additional_message):
        super(RequestProxy, self).__init__()

        self._passenger = passenger
        self._source = source
        self._destination = destination
        self._additional_message = additional_message
        self._request_id = None
        self._state = None
        self._contacts = [] 
        self._rejects = []
        self._approval = None

        self._timers = {}

        self._update_queue = []

    def __unicode__(self):
        return u'RequestProxy {0}'.format(self._passenger)

    def create(self):
        url = self.create_path
        data = { 'passenger_id': self._passenger.id, 'source_location': self._source['location'] }

        # synchronous
        payload = post(url, data)
        if payload['status'] != 'success':
            self.error('Failed to create a request entry')
        else:
            self._request_id = payload['data']['id']

        return self._request_id

    def _updatee(self):
        return {
            'state': self._state,
            'contacts': self._contacts,
            'rejects': self._rejects,
            'approval_id': self._approval,
        }

    @gen.coroutine 
    def update(self, **kwargs):
        data = self._updatee() 
        data.update(kwargs)

        self._update_queue.append(data)

        if self._request_id:
            url = self.update_path.format(pk=self._request_id)
            while self._update_queue:
                yield fetch(url, self._update_queue.pop(0))
        
        

    def add_contact(self, driver_id):
        self._contacts.append(driver_id)

        print self._updatee()

    def remove_contact(self, driver_id):
        try:
            self._contacts.remove(driver_id)
        except ValueError, e:
            self.debug('Driver {0} not in contacts, ignore remove'.format(driver_id))
        else:
            self.debug('Driver {0} removed from contact'.format(driver_id))

        print self._updatee()

    def add_reject(self, driver_id):
        self.info('Rejected driver {0}'.format(driver_id))

        # add to rejects
        self.remove_contact(driver_id)
        self._rejects.append(driver_id)

        print self._updatee()

        if self.no_contacts and self.refresh_count == 0:
            self.terminate()
    
    @property
    def no_contacts(self):
        return len(self._contacts) == 0

    def approve(self, driver_id):

        if self.approved:
            self.info('Request {0} already approved, trial by {1} failed'.format(self._request_id, driver_id))
            return False

        # cancel all timers 
        for k,v in self._timers.iteritems():

            cancel(v)

        self._approval = driver_id

        # remove from index
        DriverManager().deactivate(driver_id)

        # remove from contacts
        self.remove_contact(driver_id)
        
        # state approved
        self.info('Approve request {0}'.format(self._request_id))
        self._state = Request.APPROVED        
        self.update(state=Request.APPROVED)

           
        # make other contacts as standby, notify closed 
        for id_ in self._contacts:
            DriverManager().mark_standby(id_)

            # TODO:notify
            
        self.approved = True        
        return self.approved

    def reject(self, driver_id):
        # add to rejects
        self.add_reject(driver_id)

        # cancel timer
        cancel(self._timers[str(driver_id)])

        # index : mark standby
        DriverManager().mark_standby(driver_id)

        return True

    def terminate(self):
        self.info('Terminate request {0}'.format(self._request_id))

        # state rejected
        self._state = Request.REJECTED        
        self.update(state=Request.REJECTED)

        # mark all as standby

    def request(self):
        if self.approved:
            self.info('Request {0} approved, no more request'.format(self._request_id))
            return

        # find
        candidates = DriverManager().get_nearest_drivers(self._source['location'], self.candidate_count, 
                                                        self.max_distance, self.charge_type) 
        
        push_targets = []

        for id_, state_ in candidates:
            self.debug('Driver {id}, {state} found'.format(id=id_, state=state_))

            if state_ is None and id_ not in self._rejects and id_ not in self._contacts:
                self.info('Driver {driver_id} sent in request {request_id}'.format(driver_id=id_, request_id=self._request_id))

                self.add_contact(id_)
                DriverManager().mark_requested(id_)

                push_targets.append(id_)

        # send push
        if bool(push_targets):
            self.send_request(push_targets)

        # repeat
        self.refresh_count -= 1
        if self.refresh_count > 0:
            delay(self.refresh_interval, self.request)
        elif self.no_contacts:
            self.terminate() 

    def send_request(self, driver_ids):
        passenger = self._passenger 

        message = {
            'alert': settings.MESSAGE_RIDE_REQUEST_ALERT,
            'title': settings.MESSAGE_RIDE_REQUEST_TITLE,
            'push_type': 'ride_requested',
            'data': {
                'request_id': self._request_id,
                'passenger': { 
                    'id': passenger.id, 
                    'name': passenger.name,
                    'phone': passenger.phone,
                    'email': passenger.email,
                },
                'source': self._source,
                'destination': self._destination,
                'additional_message': self._additional_message,
            }
        }

        channels = ['driver_{id}'.format(id=id_) for id_ in driver_ids]

        send_push_notification(message, channels, False)

        # start timer
        for id_ in driver_ids:
            self._timers[str(id_)] = delay(settings.REQUEST_TIMEOUT, partial(self.add_reject, id_))

