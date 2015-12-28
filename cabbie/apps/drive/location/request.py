# encoding: utf-8
import time
from datetime import datetime, timedelta
from collections import defaultdict
from functools import partial

from django.conf import settings
from tornado import gen

from cabbie.apps.drive.models import Province, Request
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
from cabbie.utils.rand import Dice, random_int


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

        return request.approve(driver_id)
        
    def reject(self, request_id, driver_id):
        request = self._requests.get(str(request_id), None)

        if request is None:
            self.info('Request {0} gone, rejection by {1} failed'.format(request_id, driver_id))
            return False

        return request.reject(driver_id)

# 
#               PHASE_DISPATCHING                 PHASE_WAITING                  PHASE_TERMINATED
#             /                   \            /                \             /
#   dispatch                        dispatched                    termination     
#   ---------------------------------------------------------------------------------------------> time

class RequestProxy(LoggableMixin, PubsubMixin):
    """ 
    Proxy of `Request` model for asynchronous save operation
    """
    
    create_path = '/_/drive/request/create'
    update_path = '/_/drive/request/{pk}/update'

    candidate_count = settings.CANDIDATE_COUNT
    termination_delay_with_no_contact   = settings.TERMINATION_DELAY_WITH_NO_CONTACT
    termination_delay_with_contacts     = settings.TERMINATION_DELAY_WITH_CONTACTS
    charge_type = 1000
    approved = False

    PHASE_DISPATCHING, PHASE_WAITING, PHASE_TERMINATED = 'phase_dispatching', 'phase_waiting', 'phase_terminated'
   
    def __init__(self, passenger, source, destination, additional_message):
        super(RequestProxy, self).__init__()

        self._passenger = passenger
        self._source = source
        self._destination = destination
        self._additional_message = additional_message
        self._request_id = None
        self._state = None
        self._contacts = [] 
        self._contacts_detail = {}          # candidate information
        self._contacts_by_distance = {}     # by distance 
        self._rejects = []
        self._approval = None
        self._approved_candidate = None

        self._target_distances = list(settings.TARGET_DISTANCES) 
        self._border = self._target_distances[-1]
        self._phase = self.PHASE_DISPATCHING

        self._update_queue = []

        self._delayed = None
        

    def __unicode__(self):
        return u'RequestProxy {0}'.format(self._passenger)

    def create(self):
        url = self.create_path
        data = { 
            'passenger_id': self._passenger.id, 
            'source': self._source,
            'source_location': self._source['location'],
            'destination': self._destination,
            'destination_location': self._destination['location'],
        }

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
            'contacts_by_distance': self._contacts_by_distance,
            'rejects': self._rejects,
            'approval_id': self._approval,
            'approval_driver_json': self._approved_candidate,
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

    def set_contact_detail(self, driver_id, data):
        driver_id = str(driver_id)
        self._contacts_detail[driver_id] = data

    def get_contact_detail(self, driver_id):
        driver_id = str(driver_id)
        return self._contacts_detail.get(driver_id, None)


    def add_contact_by_distance(self, target_distance, driver_id):
        if self._contacts_by_distance.get(target_distance):
            self._contacts_by_distance[target_distance].append(driver_id)
        else:
            self._contacts_by_distance[target_distance] = [driver_id]

    def remove_contact(self, driver_id):
        try:
            self._contacts.remove(driver_id)
        except ValueError, e:
            self.debug('Driver {0} not in contacts, ignore remove'.format(driver_id))
        else:
            self.debug('Driver {0} removed from contact'.format(driver_id))

    def add_reject(self, driver_id):
        self.info('Rejected driver {0}'.format(driver_id))

        # add to rejects
        self.remove_contact(driver_id)
        self._rejects.append(driver_id)


    @property
    def no_contacts(self):
        return len(self._contacts) == 0

    def approve(self, driver_id):
        # return (approved, ride_id)        
        if self._state == Request.REJECTED:
            self.info('Request {0} already terminated'.format(self._request_id))
            return (False, None)

        if self.approved:
            self.info('Request {0} already approved, trial by {1} failed'.format(self._request_id, driver_id))
            return (False, None)

        if driver_id in self._rejects:
            self.info('Request {0} already rejected by {1}'.format(self._request_id, driver_id))
            return (False, None)

        # cancel terminate timer
        self.cancel_delayed()

        # remove from contacts
        self.remove_contact(driver_id)
        
        # Fetch the last driver info before deactivating
        driver_location = DriverManager().get_driver_location(driver_id)
        driver_charge_type = DriverManager().get_driver_charge_type(driver_id)

        # remove from index
        DriverManager().deactivate(driver_id)

        # Create a new ride proxy instance from information in approved request
        proxy = RideProxyManager().create(self._passenger.id, self._source, self._destination, self._additional_message)
        proxy.set_driver(driver_id, driver_location, driver_charge_type)

        # notify to driver
        proxy.request()

        candidate = self.get_contact_detail(driver_id)
        self.debug('Approved candidate: {0}'.format(candidate))
        proxy.approve(candidate)     # send push at this timing


        # state approved
        self.info('Approve request {0}'.format(self._request_id))
        self._approval = proxy._ride_id 
        self._state = Request.APPROVED        
        self._approved_candidate = candidate
        self.update(state=Request.APPROVED)

           
        # make other contacts as standby, notify closed 
        for id_ in self._contacts:
            DriverManager().mark_standby(id_)

        # notify expired to others
        self.send_expired(self._contacts) 
            
        self.approved = True        
        return (self.approved, proxy._ride_id)

    def reject(self, driver_id):
        # index : mark standby
        DriverManager().mark_standby(driver_id)

        # add to rejects
        self.add_reject(driver_id)

        # early termination if rejected all
        if self._phase == self.PHASE_WAITING and self.get_current_contacts() == 0:
            self.terminate()

        return True

    def terminate(self):
        if self._state == Request.REJECTED:
            self.info('Terminate request {0} but already terminated'.format(self._request_id))
            return

        # terminate
        self.info('Terminate request {0}'.format(self._request_id))

        # phase transition
        self.transit_phase(self.PHASE_TERMINATED)

        # cancel delayed
        self.cancel_delayed()

        # make other contacts as standby
        for id_ in self._contacts:
            DriverManager().mark_standby(id_)

        # state rejected
        self._state = Request.REJECTED        
        self.update(state=Request.REJECTED)

        # notify others that this request has been expired 
        self.send_expired(self._contacts) 

    @gen.coroutine
    def start(self):
        self.set_delayed_request(immediate=True) 


    @gen.coroutine
    def request(self, target_distance):
        if self.approved:
            self.info('Request {0} approved, no more request'.format(self._request_id))
            return

        # find
        candidates = yield DriverManager().get_driver_candidates(self._passenger.id, self._source['location'], self.candidate_count, 
                                                        target_distance, self.charge_type) 

        self.info('Request {0} within {1}m: {2}'.format(self._request_id, target_distance, candidates))

        push_targets = []

        for candidate in candidates:
            driver_ = candidate['driver']

            if driver_ is None:     # dropped-out driver
                self.info('Ignore driver since it\'s dropped out')
                continue

            id_ = driver_['id']
            location_ = candidate['location']

            # province rule
            if not self.is_allowed_area(driver_):
                self.info('Ignore driver {id} since its business area is not matched with source, destination'.format(id=id_))
                continue
            

            if location_ is None:
                self.info('Ignore driver {id} since its location is not found'.format(id=id_))
                continue

            valid_location = self.is_valid_location(self._source['location'], location_, id_, target_distance) 

            if not valid_location:
                continue

            is_freezed = driver_['is_freezed']

            if is_freezed:
                self.info('Ignore driver {id} since it\'s freezed'.format(id=id_))
                continue

            state_ = candidate['state']
            candidate['estimate'] = candidate['estimate'].for_json()

            if state_ is None and id_ not in self._rejects and id_ not in self._contacts:
                self.info('Driver {driver_id} sent in request {request_id}'.format(driver_id=id_, request_id=self._request_id))

                self.add_contact(id_)

                self.add_contact_by_distance(target_distance, id_)

                # cache contact info
                self.set_contact_detail(id_, candidate)

                DriverManager().mark_requested(id_)

                push_targets.append(id_)

        # send push
        if bool(push_targets):
            self.debug('{0}m targets: {1}'.format(target_distance, push_targets))

            self.send_request(push_targets)

        # phase : PHASE_DISPATCHING --> PHASE_WAITING at edge boundary
        if target_distance == self._border:
            self.transit_phase(self.PHASE_WAITING)

        self.set_delayed_request()        


    def set_delayed_request(self, immediate=False):
        target_distance = self.get_target_distance()

        if target_distance is None:
            # terminate
            if self.get_current_contacts() == 0:
                self.terminate()
            else:
                self._delayed = delay(self.termination_delay_with_contacts, self.terminate)
            return

        if immediate:
            self.request(target_distance)
        else:
            delay_time = self.guess_delay_time()
            self._delayed = delay(delay_time, partial(self.request, target_distance))

    def cancel_delayed(self):
        if self._delayed:
            self.info('Cancel delayed request')
            cancel(self._delayed)

    def get_target_distance(self):
        if bool(self._target_distances):
            return self._target_distances.pop(0)
        else:
            return None

    def guess_delay_time(self):
        current_contacts = self.get_current_contacts() 

        if current_contacts == 0:
            return 0
        elif current_contacts <= 5:
            return 5
        elif current_contacts >= 10:
            return 10
        else:
            return current_contacts * 1

    def get_current_contacts(self):
        return len(self._contacts)

    def transit_phase(self, new):
        if self._phase == new:
            self.info('Already in {0} phase'.format(self._phase))
        else:
            old = self._phase
            self._phase = new
            self.info('Phase transtion from {0} to {1}'.format(old, new))


    def is_valid_location(self, source_location, driver_location, driver_id, target_distance):
        distance_ = distance(source_location, driver_location)
        if distance_ > target_distance:
            self.error('Driver {0} location {1} is invalid, because distance is {2}, and it\'s far from source {3} beyond {4}m'
                        .format(driver_id, driver_location, distance_, source_location, target_distance))
            return False
        else:
            self.info('Driver {0} location {1} is valid, because distance is {2}, and it\'s within {3}m from source {4}'
                        .format(driver_id, driver_location, distance_, target_distance, source_location))
            return True


    def is_allowed_area(self, driver):
        source_address = self._source.get('address')
        source_poi = self._source.get('poi')
        destination_address = self._destination.get('address')
        destination_poi = self._destination.get('poi')
        
        if not source_address or not destination_address:
            return False
    
        route = ((source_address, destination_address), (source_poi, destination_poi))

        _driver_business_area = self.driver_business_area(driver, route)
        allowed = self.is_business_area(_driver_business_area, route)

        if isinstance(_driver_business_area, basestring):
            _driver_business_area = [_driver_business_area]

        self.debug('[AREA] R{request_id}-D{driver_id}, Allowed? {allowed}, populated area: {populated_area}'
                    .format(request_id=self._request_id, driver_id=driver['id'], allowed=allowed, populated_area=','.join(_driver_business_area)))
    
        return allowed

    def driver_business_area(self, driver, route):
        """
        Populate driver's business area
        
        Route affects due to exceptional cases
        """
        # basic rule
        _area = driver['province']

        if _area in Province.PROVINCES_REQUIRING_REGION:
            _area += ' ' + driver['region']

        # exception 1 in address: 경기 광명시 & [서울 구로구, 서울 금천구]
        exceptional_area = u'경기 광명시'
        counter_area = [u'서울 구로구', u'서울 금천구']

        if self.compare_area(exceptional_area, route[0]) and _area == u'서울':
            _area = [_area, exceptional_area]

        if self.compare_area(counter_area, route[0]) and _area == exceptional_area:
            _area = [_area] + counter_area

        # exception 2 in address: 경기 안양시, 과천시, 의왕시, 군포시        
        exceptional_area = [u'경기 안양시', u'경기 과천시', u'경기 의왕시', u'경기 군포시']
        if self.compare_area(exceptional_area, route[0]) and _area in exceptional_area:
            _area = exceptional_area

        # exception in poi: [인천공항, 인천국제공항, 김포공항, 김포국제공항] & [서울, 경기 부천시, 인천]
        exceptional_area = [u'인천공항', u'인천국제공항', u'김포공항', u'김포국제공항']

        if self.compare_area(exceptional_area, route[1], source_only=True):
            _area = [_area] + exceptional_area


        self.debug('#{driver_id} driver\'s business area populated from {route}: {area}'.format(driver_id=driver['id'], route=route, area=_area))
            
        return _area

    def is_business_area(self, business_area, route):
        if isinstance(business_area, basestring):
            business_area = [business_area]

        return any([self.compare_area(area, route[0]) for area in business_area]) or any([self.compare_area(area, route[1]) for area in business_area])

    def compare_area(self, area, route, source_only=False):
        """
        Compare area with route
            
        Param
            area: basestring or list of basestring, which indicates business area
            route: (source_address, destination_address) or (source_poi, destination_poi)
            source_only: check only source if set to True, default=False

        Return
            True when route matches with at least one area
        """
        if isinstance(area, basestring):
            area = [area]
        area_list = area 

        if source_only:
            return any([area == route[0][:len(area)] for area in area_list])
        else:
            return any([area == route[0][:len(area)] or area == route[1][:len(area)] for area in area_list])


    def send_request(self, driver_ids):
        passenger = self._passenger 

        now = datetime.now()
    
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
                'created_at': str(now), 
                'expires_at': str(now + timedelta(seconds=settings.REQUEST_TIMEOUT)),
            }
        }

        channels = ['driver_{id}'.format(id=id_) for id_ in driver_ids]

        send_push_notification(message, channels)


    def send_expired(self, driver_ids):
        message = {
            'alert': settings.MESSAGE_RIDE_EXPIRED_ALERT,
            'title': settings.MESSAGE_RIDE_EXPIRED_TITLE,
            'push_type': 'ride_expired',
            'data': {
                'request_id': self._request_id,
            }
        }

        channels = ['driver_{id}'.format(id=id_) for id_ in driver_ids]

        send_push_notification(message, channels)


