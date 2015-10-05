# encoding: utf8

from django.db import models
from django.utils import timezone

from cabbie.common.models import AbstractTimestampModel
from cabbie.common.fields import JSONField

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
        passengers_by_date = self.applied_passengers.get(date)

        if not passengers_by_date:
            return False 
        
        ride_ids = passengers_by_date.get(passenger.id)

        if not ride_ids:
            return False 

        return len(ride_ids) < limit_count

    def update_event(self, date, ride):
        passengers_by_date = self.applied_passengers.get(date)

        if not passengers_by_date:
            passenger_ride_ids = {}
            passenger_ride_ids[ride.passenger.id] = [ride.id]
            self.applied_passengers[date] = passenger_ride_ids
        else:
            ride_ids = passenger_by_date.get(ride.passenger.id)

            if not ride_ids:
                passenger_by_date[ride.passenger.id] = [ride.id]
            else:
                passenger_by_date[ride.passenger.id] = ride_ids.append(ride.id)

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


