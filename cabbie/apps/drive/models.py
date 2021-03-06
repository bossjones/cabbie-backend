# encoding: utf8
import datetime, time

from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from cabbie.apps.account.models import Passenger, Driver
from cabbie.apps.drive.managers import TimezoneManager
from cabbie.apps.drive.signals import post_request_rejected, post_ride_approve, post_ride_reject, post_ride_cancel, post_ride_arrive, post_ride_board, post_ride_complete, post_ride_first_rated, post_ride_rated
from cabbie.common.fields import JSONField
from cabbie.common.models import AbstractTimestampModel, IncrementMixin
from cabbie.utils import json
from cabbie.utils.geo import distance
from cabbie.utils.crypto import encrypt
from cabbie.utils.email import send_email


class Province(models.Model):
    name = models.CharField(u'시도', max_length=20, primary_key=True)

    def __unicode__(self):
        return u'{name}'.format(name=self.name)

    class Meta:
        verbose_name = u'시도'
        verbose_name_plural = u'시도'


class Region(models.Model):
    name = models.CharField(u'지역', max_length=30)
    depth = models.PositiveIntegerField(u'Depth', default=0) 
    province = models.ForeignKey(Province, related_name='regions', verbose_name=u'시도')
    parent = models.ForeignKey('self', related_name='childs', verbose_name=u'상위지역'
                                    , null=True, blank=True, on_delete=models.SET_NULL)

    def __unicode__(self):
        return u'{name}'.format(name=self.name)

    class Meta:
        verbose_name = u'지역'
        verbose_name_plural = u'지역'



class Request(AbstractTimestampModel):
    STANDBY, APPROVED, REJECTED,  = 'standby', 'approved', 'rejected'

    STATES = (
        (STANDBY, _('standby')),
        (APPROVED, _('approved')),
        (REJECTED, _('rejected')),
    )

    STATE_EXPRESSION = { 
        STANDBY: u'요청중',
        APPROVED: u'승인',
        REJECTED: u'차량없음',
    }

    passenger = models.ForeignKey(Passenger, related_name='requests', verbose_name=u'승객'
                                            , null=True, on_delete=models.SET_NULL)
    # source
    source = JSONField(u'출발지', default='{}')
    source_location = models.PointField(u'출발지 좌표')
    source_province = models.ForeignKey(Province, related_name='requests', verbose_name=u'콜요청 지역'
                                                , null=True, blank=True, on_delete=models.SET_NULL)
    source_region1 = models.ForeignKey(Region, related_name='depth1_request_regions', verbose_name=u'콜요청 세부지역1'
                                                , null=True, blank=True, on_delete=models.SET_NULL)
    source_region2 = models.ForeignKey(Region, related_name='depth2_request_regions', verbose_name=u'콜요청 세부지역2'
                                                , null=True, blank=True, on_delete=models.SET_NULL)

    # distance
    destination = JSONField(u'도착지', default='{}')
    destination_location = models.PointField(u'도착지 좌표', blank=True,
                                             null=True)
    destination_province = models.ForeignKey(Province, related_name='destinations', verbose_name=u'도착지 지역'
                                                    , null=True, blank=True, on_delete=models.SET_NULL)
    destination_region1 = models.ForeignKey(Region, related_name='depth1_destination_regions', verbose_name=u'도착지 세부지역1'
                                                , null=True, blank=True, on_delete=models.SET_NULL)
    destination_region2 = models.ForeignKey(Region, related_name='depth2_destination_regions', verbose_name=u'도착지 세부지역2'
                                                , null=True, blank=True, on_delete=models.SET_NULL)

    distance = models.PositiveIntegerField(u'요청거리', default=0)

    state = models.CharField(u'상태', max_length=50, choices=STATES)
    contacts = JSONField(u'보낸기사', default='[]')
    contacts_by_distance = JSONField(u'거리별 보낸기사', default='{}')
    rejects = JSONField(u'거절기사', default='[]')
    approval = models.ForeignKey('Ride', blank=True, null=True, related_name='approved_request', verbose_name=u'승인된 배차'
                                                            , on_delete=models.SET_NULL)
    approval_driver_json = JSONField(u'승인기사 데이터', blank=True, null=True)

    objects = models.GeoManager()

    objects_with_tz_normalizer = TimezoneManager()

    class Meta(AbstractTimestampModel.Meta):
        verbose_name = u'배차 요청'
        verbose_name_plural = u'배차 요청'

    def __unicode__(self):
        return u'{id}'.format(id=self.id)

    # source
    def source_address(self):
        return self.source.get('address', '')
    source_address.short_description = u'출발지 주소'
    source_address = property(source_address)

    def source_poi(self):
        return self.source.get('poi', '')
    source_poi.short_description = u'출발지 POI'
    source_poi = property(source_poi)

    # for admin
    def source_information(self):
        return self.source_poi + u'<br />' + self.source_address if self.source_poi and self.source_address else '' 
    source_information.short_description = u'출발지 정보'
    source_information.allow_tags = True

    # destination
    def destination_address(self):
        return self.destination.get('address', '')
    destination_address.short_description = u'도착지 주소'
    destination_address = property(destination_address)

    def destination_poi(self):
        return self.destination.get('poi', '')
    destination_poi.short_description = u'도착지 POI'
    destination_poi = property(destination_poi)

    # for admin
    def destination_information(self):
        return self.destination_poi + u'<br />' + self.destination_address if self.destination_poi and self.destination_address else ''
    destination_information.short_description = u'도착지 정보'
    destination_information.allow_tags = True

    def description_for_contacts_by_distance(self):
        ret = str()

        sorted_keys = sorted(int(key) for key in self.contacts_by_distance.keys())

        for distance_ in sorted_keys:
            contacts_ = self.contacts_by_distance.get(str(distance_))
            desc = u'{distance}m: {contacts}'.format(distance=distance_, contacts=','.join(self._decorate_contact(v) for v in contacts_))
            desc += u'<br />'
            ret += desc
        return ret
    description_for_contacts_by_distance.short_description = u'거리별 콜요청 리스트'
    description_for_contacts_by_distance.allow_tags = True

    
    def parse_source(self):
        return Request.parse_address(self.source.get('address'))

    def parse_destination(self):
        return Request.parse_address(self.destination.get('address')) 
   
    @staticmethod
    def parse_address(address):
        """
        Parse address string and return a tuple (province, region1, region2)
        """
        province = None
        region1 = None
        region2 = None

        if not address or not isinstance(address, basestring):
            return (province, region1, region2)
            
        addresses = address.split() 

        # province
        try:
            province = addresses[0]
        except IndexError, e:
            pass

        # region1
        try:
            region1 = addresses[1]
        except IndexError, e:
            pass

        # region2
        try:
            region2 = addresses[2]
        except IndexError, e:
            pass

        return (province, region1, region2)


    def _decorate_contact(self, contact):
        if contact in self.rejects:
            return '<font color=#aaaaaa>{0}</font>'.format(contact)
        if self.approval and self.approval.driver and contact == self.approval.driver.id:
            return '<font color=#51c692>{0}</font>'.format(contact)
        return str(contact)  

    # property state_kor
    def _state_kor(self):
        return Request.STATE_EXPRESSION[self.state]
    _state_kor.short_description = u'상태'
    state_kor = property(_state_kor)


    def update(self, **data):
        for field in ('state', 'contacts', 'contacts_by_distance', 'rejects', 'approval_id', 'approval_driver_json'): 
            value = data.get(field)
            if value:
                setattr(self, field, value)
    
        self.save()

        if self.state == self.REJECTED:
            post_request_rejected.send(sender=self.__class__, request=self)

    def get_normalized_rep(self):
        for normalized in self.normalized.all():
            if normalized.is_representative:
                return normalized
        return None
 

class RequestNormalized(AbstractTimestampModel):
    ref = models.ForeignKey(Request, related_name='normalized', verbose_name=u'배차요청'
                                            , null=True, on_delete=models.SET_NULL)
    parent = models.ForeignKey('self', related_name='childs', verbose_name=u'부모'
                                    , null=True, blank=True, on_delete=models.SET_NULL)
    reason = models.CharField(u'Reason', max_length=100, default='')

    class Meta(AbstractTimestampModel.Meta):
        verbose_name = u'배차 요청 Normalization'
        verbose_name_plural = u'배차 요청 Normalization'

    def __unicode__(self):
        return u'{id}'.format(id=self.id)

    @property
    def is_representative(self):
        return self.parent is None
    
    def is_approved(self):
        if self.ref.approval:
            return True

        for normalized in self.childs.all():
            if normalized.ref.approval:
                return True 
        return False

    def is_completed(self):
        if self.ref.approval and self.ref.approval.state in (Ride.BOARDED, Ride.COMPLETED, Ride.RATED):
            return True

        for normalized in self.childs.all():
            if normalized.ref.approval and normalized.ref.approval.state in (Ride.BOARDED, Ride.COMPLETED, Ride.RATED):
                return True
        return False

    @staticmethod
    def normalize(request):
        # find normalization group
        rep, reason = RequestNormalized.find_normalized(request)
        print reason

        if rep:
            # append
            RequestNormalized(ref=request, parent=rep, reason=reason).save()
        else:
            # new
            RequestNormalized(ref=request, reason=reason).save()

    @staticmethod
    def find_normalized(request):
        # 1. rep
        try:
            rep = RequestNormalized.objects.filter(ref__passenger=request.passenger, parent=None).latest('created_at')
        except RequestNormalized.DoesNotExist, e:
            return None, 'Request {req} has no rep'.format(req=request.id)
        else:
            # 2. within 1 hour from rep
            if rep.ref.created_at + datetime.timedelta(hours=1) <= request.created_at:
                return None, 'Request {req} is more than one hour later than rep'.format(req=request.id)

            # 3. source < 500m, destination < 500m
            # source
            if not request.source_location or not rep.ref.source_location:
                return None, 'Request {req} source or its rep source has no location information'.format(req=request.id)

            if 500 < distance(request.source_location, rep.ref.source_location): 
                return None, 'Request {req} source is more than 500m far away'.format(req=request.id)

            # destination
            if not request.destination_location or not rep.ref.destination_location:
                return None, 'Request {req} destination or its rep destination has no location information'.format(req=request.id)

            if 500 < distance(request.destination_location, rep.ref.destination_location):
                return None, 'Request {req} destination is more than 500m far away'.format(req=request.id)


            return rep, 'Rep request {req} found'.format(req=rep.ref.id)


    @staticmethod
    def get_normalized_count(queryset):
        count = 0
        for request in queryset.all():
            normalized_rep = request.get_normalized_rep()
            if normalized_rep:
                count += 1
        return count

    @staticmethod
    def get_approved_normalized_count(queryset):
        count = 0
        for request in queryset.all():
            normalized_rep = request.get_normalized_rep()
            if normalized_rep and normalized_rep.is_approved():
                count += 1
        return count

    @staticmethod
    def get_completed_normalized_count(queryset):
        count = 0
        for request in queryset.all():
            normalized_rep = request.get_normalized_rep()
            if normalized_rep and normalized_rep.is_completed():
                count += 1
        return count


class Ride(IncrementMixin, AbstractTimestampModel):
    REQUESTED, APPROVED, REJECTED, CANCELED, DISCONNECTED, ARRIVED, BOARDED, \
        COMPLETED, RATED = \
    'requested', 'approved', 'rejected', 'canceled', 'disconnected', \
        'arrived', 'boarded', 'completed', 'rated'
    STATES = (
        (REQUESTED, _('requested')),
        (APPROVED, _('approved')),
        (REJECTED, _('rejected')),
        (CANCELED, _('canceled')),
        (DISCONNECTED, _('disconnected')),
        (ARRIVED, _('arrived')),
        (BOARDED, _('boarded')),
        (COMPLETED, _('completed')),
        (RATED, _('rated')),
    )

    STATE_EXPRESSION = { 
        REQUESTED: u'요청',
        APPROVED: u'승인',
        REJECTED: u'기사거절',
        CANCELED: u'승객취소',
        DISCONNECTED: u'연결끊김',
        ARRIVED: u'픽업도착',
        BOARDED: u'탑승',
        COMPLETED: u'운행완료',
        RATED: u'평가완료',
    }

    IMMEDIATE, TIMEOUT, AFTER, WAITING, UNSHOWN = \
    'immediate', 'timeout', 'after', 'waiting', 'unshown'

    REASONS = (
        (IMMEDIATE, _('immediate')),
        (TIMEOUT, _('timeout')),
        (AFTER, _('after')),
        (WAITING, _('waiting')),
        (UNSHOWN, _('unshown')),
    )

    REASON_EXPRESSION = {
        IMMEDIATE: u'즉시거절',
        TIMEOUT: u'30초 타임아웃',
        AFTER: u'탑승이전 취소',
        WAITING: u'대기중 취소',
        UNSHOWN: u'승객 나타나지 않음',
    }

    passenger = models.ForeignKey(Passenger, related_name='rides',
                                  verbose_name=u'승객', null=True, on_delete=models.SET_NULL)
    driver = models.ForeignKey(Driver, blank=True, null=True,
                               related_name='rides', verbose_name=u'기사', on_delete=models.SET_NULL)

    state = models.CharField(u'상태', max_length=100, choices=STATES)

    # Additional message
    additional_message = JSONField(u'추가메세지', default='{}')

    # Reject reason
    reason = models.CharField(u'거절이유', max_length=20, choices=REASONS)

    # Ride detail
    source = JSONField(u'출발지')
    source_location = models.PointField(u'출발지 좌표')
    destination = JSONField(u'도착지', default='{}')
    destination_location = models.PointField(u'도착지 좌표', blank=True,
                                             null=True)
    charge_type = models.PositiveIntegerField(u'콜비', blank=True)
    summary = JSONField(u'요약', default='{}')

    # Rating
    ratings_by_category = JSONField(u'상세평점', default='{}')
    comment = models.CharField(u'코멘트', max_length=100, blank=True)

    objects = models.GeoManager()

    objects_with_tz_normalizer = TimezoneManager()

    class Meta(AbstractTimestampModel.Meta):
        verbose_name = u'배차'
        verbose_name_plural = u'배차'

    def __unicode__(self):
        return u'{id}'.format(id=self.id)

    def source_address(self):
        return self.source.get('address', '')
    source_address.short_description = u'출발지 주소'
    source_address = property(source_address)

    def source_poi(self):
        return self.source.get('poi', '')
    source_poi.short_description = u'출발지 POI'
    source_poi = property(source_poi)

    def destination_address(self):
        return self.destination.get('address', '')
    destination_address.short_description = u'도착지 주소'
    destination_address = property(destination_address)

    def destination_poi(self):
        return self.destination.get('poi', '')
    destination_poi.short_description = u'도착지 POI'
    destination_poi = property(destination_poi)

    def get_incrementer(self, reverse=False):
        incrementer = super(Ride, self).get_incrementer(reverse)
        return incrementer

    @property
    def _created_at_in_local_time(self):
        return timezone.get_current_timezone().normalize(self.created_at)

    def is_educated_driver(self):
        if self.driver and self.driver.education:
            return self.created_at > self.driver.education.started_at
        return False

    # property state_kor
    def _state_kor(self):
        return Ride.STATE_EXPRESSION[self.state]
    _state_kor.short_description = u'상태'
    state_kor = property(_state_kor)

    # property reason_kor
    def _reason_kor(self):
        return Ride.REASON_EXPRESSION.get(self.reason, '')
    _reason_kor.short_description = u'거절이유'
    reason_kor = property(_reason_kor)


    # property rating
    def _rating(self):
        total_rating = 0
        count = 0

        for key, value in self.ratings_by_category.iteritems():
            total_rating += int(value)
            if value > 0:
                count += 1

        return 0.0 if count == 0 else float(total_rating) / count 
    _rating.short_description = u'평점'
    rating = property(_rating)


    # category rating
    def _rating_kindness(self):
        return self.ratings_by_category.get('kindness', None)
    _rating_kindness.short_description = u'친절'
    rating_kindness = property(_rating_kindness)

    def _rating_cleanliness(self):
        return self.ratings_by_category.get('cleanliness', None)
    _rating_cleanliness.short_description = u'청결'
    rating_cleanliness = property(_rating_cleanliness)

    def _rating_security(self):
        return self.ratings_by_category.get('security', None)
    _rating_security.short_description = u'안전'
    rating_security = property(_rating_security)




    def rate(self, ratings_by_category, comment):
        old_ratings_by_category = self.ratings_by_category

        self.ratings_by_category = ratings_by_category
        self.comment = comment
        update_fields = ['ratings_by_category', 'comment']

        # state 
        is_new  = self.state != self.RATED
        if is_new:
            self.state = self.RATED
            update_fields.extend(['state'])

        self.save(update_fields=update_fields)

        # signal for stat, point
        post_ride_rated.send(sender=self.__class__, ride=self)

        if is_new:
            post_ride_first_rated.send(sender=self.__class__, ride=self)

    def transit(self, **data):

        old_state = self.state

        for field in ('state', 'driver_id', 'charge_type', 'summary', 'reason'):
            value = data.get(field)
            if value:
                setattr(self, field, value)
    
        if self.state == self.ARRIVED:
            return

        if self.state == old_state:
            return

        # ignore ride update when already rated
        if old_state == self.RATED:
            pass
        else:
            self.save()

        # create history
        passenger_location = (Point(*data['passenger_location'])
                              if 'passenger_location' in data else None)
        driver_location = (Point(*data['driver_location'])
                           if 'driver_location' in data else None)

        self.histories.create(
            created_at=self.created_at,
            updated_at=self.updated_at,
            driver=self.driver,
            state=self.state,
            passenger_location=passenger_location,
            driver_location=driver_location,
            data=data,
        )

        if self.state == self.APPROVED:
            post_ride_approve.send(sender=self.__class__, ride=self)

        elif self.state == self.REJECTED:
            post_ride_reject.send(sender=self.__class__, ride=self)

        elif self.state == self.CANCELED:
            post_ride_cancel.send(sender=self.__class__, ride=self)

        elif self.state == self.ARRIVED:
            post_ride_arrive.send(sender=self.__class__, ride=self)

        elif self.state == self.BOARDED:
            post_ride_board.send(sender=self.__class__, ride=self)

        elif self.state == self.COMPLETED:
            if old_state != self.RATED:
                post_ride_complete.send(sender=self.__class__, ride=self)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super(Ride, self).save(
            force_insert, force_update, using, update_fields)


class RideHistory(AbstractTimestampModel):
    ride = models.ForeignKey(Ride, related_name='histories',
                             verbose_name=u'배차')
    driver = models.ForeignKey(Driver, blank=True, null=True,
                               related_name='ride_histories',
                               verbose_name=u'기사')

    state = models.CharField(u'상태', max_length=100, choices=Ride.STATES)
    passenger_location = models.PointField(u'승객 좌표')
    driver_location = models.PointField(u'기사 좌표', blank=True, null=True)
    data = JSONField(u'데이터', default='{}')

    def __unicode__(self):
        return u'Ride {0}: {1}'.format(self.ride.id, self.state)

    class Meta(AbstractTimestampModel.Meta):
        verbose_name = u'배차 이력'
        verbose_name_plural = u'배차 이력'

    def _is_admin(self):
        return self.data.get('admin', False)
    _is_admin.short_description = u'어드민'
    is_admin = property(_is_admin)

class Favorite(AbstractTimestampModel):
    passenger = models.ForeignKey(Passenger, related_name='favorites',
                                  verbose_name=u'승객')
    name = models.CharField(u'이름', max_length=100)
    location = models.PointField(u'좌표')
    address = models.CharField(u'주소', max_length=1000, blank=True,
                               db_index=True)
    poi = models.CharField(u'POI', max_length=1000, blank=True)

    objects = models.GeoManager()

    class Meta(AbstractTimestampModel.Meta):
        verbose_name = u'즐겨찾기'
        verbose_name_plural = u'즐겨찾기'


class Hotspot(AbstractTimestampModel):
    location = models.PointField(u'좌표',
                                 help_text=u'경도와 위도를 한줄씩 입력하세요')
    address = models.CharField(u'주소', max_length=1000, blank=True,
                               db_index=True)
    poi = models.CharField(u'POI', max_length=1000, blank=True)
    ride_count = models.PositiveIntegerField(u'배차횟수', default=0)
    weight = models.IntegerField(u'가중치', db_index=True,
                                 help_text=u'높을수록 상위에 노출됩니다')
    is_promotion = models.BooleanField(u'프로모션', default=True)

    class Meta(AbstractTimestampModel.Meta):
        verbose_name = u'인기장소'
        verbose_name_plural = u'인기장소'


from cabbie.apps.drive.receivers import *
