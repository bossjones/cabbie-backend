# encoding: utf8
import requests

from django.db import models
from django.utils import timezone

from cabbie.common.models import AbstractTimestampModel
from cabbie.common.fields import JSONField

from cabbie.apps.account.models import Passenger

# Types
EVENT_CU = 'cu'

class RidePointEvent(AbstractTimestampModel):
    name = models.CharField(u'이름', max_length=20)
    starts_at = models.DateTimeField(u'시작시각', default=timezone.now)
    ends_at = models.DateTimeField(u'종료시각', default=timezone.now)
    is_first_come_first_served_basis = models.BooleanField(u'선착순 여부', default=False)
    capacity = models.PositiveIntegerField(u'대상 건수 (선착순일 때만 적용)', default=0)
    event_point = models.PositiveIntegerField(u'지급 예정 포인트')
    applied_count = models.PositiveIntegerField(u'적용수', default=0) 
    is_accomplished = models.BooleanField(u'달성여부 (선착순일 때만 적용)', default=False)
    priority = models.PositiveIntegerField(u'우선순위', unique=True)

    # further specification types
    SPEC_TYPE_NONE, SPEC_TYPE_LIMITED_PER_DAY, SPEC_TYPE_LIMITED_PER_PERSON = 'none', 'limited_per_day', 'limited_per_person'

    SPECIFICATION_TYPES = (
        (SPEC_TYPE_NONE, u'없음'),
        (SPEC_TYPE_LIMITED_PER_DAY, u'일당 횟수제한'),
        (SPEC_TYPE_LIMITED_PER_PERSON, u'인당 횟수제한'),
    )

    specification_type = models.CharField(u'조건', max_length=20, choices=SPECIFICATION_TYPES, default=SPEC_TYPE_NONE)
    specification_limit_count = models.PositiveIntegerField(u'수', default=0)
    
    # for deep analysis
    applied_passengers = JSONField(u'관련된 승객들', default='{}')    # { 'date' : { 'passenger_id' : [ride_id, ...] }, ... }

    class Meta(AbstractTimestampModel.Meta):
        verbose_name = u'탑승 포인트 이벤트'
        verbose_name_plural = u'탑승 포인트 이벤트'

    @staticmethod
    def current_event():
        now = timezone.now 
        current_events = RidePointEvent.objects.filter(starts_at__lte=now, ends_at__gt=now, is_accomplished=False).order_by('priority')

        if len(current_events) == 0:
            return None

        return current_events[0]

    def check_if_applicable_passenger_by_date(self, passenger, date, limit_count):
        date_key = date.strftime('%Y-%m-%d')
        passengers_by_date = self.applied_passengers.get(date_key)

        if not passengers_by_date:
            return True 
        
        passenger_key = str(passenger.id)
        ride_ids = passengers_by_date.get(passenger_key)

        if not ride_ids:
            return True 

        return len(ride_ids) < limit_count

    def update_event(self, date, ride):
        date_key = date.strftime('%Y-%m-%d')
        passengers_by_date = self.applied_passengers.get(date_key)
        
        passenger_key = str(ride.passenger.id)

        if not passengers_by_date:
            passengers_by_date= {}
            passengers_by_date[passenger_key] = [ride.id]
            self.applied_passengers[date_key] = passengers_by_date 
        else:
            ride_ids = passengers_by_date.get(passenger_key)

            if not ride_ids:
                passengers_by_date[passenger_key] = [ride.id]
            else:
                ride_ids.append(ride.id)
                passengers_by_date[passenger_key] = ride_ids

            self.applied_passengers[date_key] = passengers_by_date

        self.applied_count += 1

        update_fields = ['applied_passengers', 'applied_count']

        # check if accomplished
        if self.is_first_come_first_served_basis and self.applied_count >= self.capacity:
            self.is_accomplished = True
            update_fields.append('is_accomplished')

        self.save(update_fields=update_fields)



    def apply_event(self, ride):
        # check specification
        today = timezone.datetime.today()
        is_target = False

        if not ride.passenger:
            is_target = False

        elif self.specification_type == RidePointEvent.SPEC_TYPE_NONE:
            is_target = True
            
        elif self.specification_type == RidePointEvent.SPEC_TYPE_LIMITED_PER_DAY: 
            # check applied_passengers 
            is_target = self.check_if_applicable_passenger_by_date(ride.passenger, today, self.specification_limit_count) 

        elif self.specification_type == RidePointEvent.SPEC_TYPE_LIMITED_PER_PERSON: 
            # check applied_passengers
            # TODO: not implemented yet
            pass


        if not is_target:
            # this passenger is not the target of this event, propagate
            return False

        # update applied_count, is_accomplished, applied_passengers
        self.update_event(today, ride)

        return True


class CuEventCode(models.Model):
    code = models.CharField(u'코드', max_length=10) 

    class Meta:
        verbose_name = u'CU 이벤트코드'
        verbose_name_plural = u'CU 이벤트코드'


class CuEventPassengers(AbstractTimestampModel):
    passenger = models.OneToOneField(Passenger, related_name='cu_event', blank=True, null=True, on_delete=models.SET_NULL)
    code = models.CharField(u'코드', max_length=10) 
    is_gift_sent = models.BooleanField(u'기프티콘 발송여부', default=False)
    gift_sent_at = models.DateTimeField(u'기프티콘 발송시각', blank=True, null=True)

    pin_no = models.CharField(u'바코드번호', max_length=30, blank=True, null=True)
    api_response_code = models.CharField(u'API응답코드', max_length=2, blank=True, null=True)

    res_msg = models.CharField(u'응답메시지', max_length=100, blank=True, null=True)

    auth_id = models.CharField(u'승인번호', max_length=20, blank=True, null=True)
    auth_date = models.CharField(u'승인일자', max_length=20, blank=True, null=True)

    is_issue_canceled = models.BooleanField(u'발행취소여부', default=False) 

    class Meta(AbstractTimestampModel.Meta):
        verbose_name = u'CU 코드입력 승객'
        verbose_name_plural = u'CU 코드입력 승객'

    def make_gift_sent(self, sent=True):
        if sent:
            self.is_gift_sent = True
            self.gift_sent_at = timezone.now()
        else:
            self.is_gift_sent = False
            self.gift_sent_at = None
        self.save(update_fields=['is_gift_sent', 'gift_sent_at'])

    def cancel_gift_issue(self):
        if self.auth_id and self.auth_date:
            # url
            url = 'http://{host_port}'.format(host_port=settings.CU_GIFT_SERVER)
            path = 'cu/linkPublishLimit.do'

            # data 
            data = {}
            data['COM_KEY'] = '186'
            data['SEL_PRD_NO'] = '2015111001'                   # TODO: changed later 
            data['ORD_NO'] = str(self.id)                       # any unique number within bktaxi
            data['TRAN_GB'] = '1'   # '0': issue, '1': cancel, '2': PIN issue, '3': PIN cancel
            data['ISSUE_APP_NO'] = self.auth_id 
            data['ISSUE_APP_DAY'] = self.auth_date[:8]
            data['CANCEL_GB'] = '0'
            data['PIN_YN'] = '0'
            data['ORD_QTY'] = '1'
            data['BUY_PRC'] = '1520'

            response = requests.post(url + '/' + path, data=data)
            print response.text

            self.is_issue_canceled = True
            self.save(update_fields=['is_issue_canceled'])


from cabbie.apps.event.receivers import *
