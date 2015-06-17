# encoding: utf8

import datetime

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import F, Q
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from cabbie.apps.education.models import Education
from cabbie.apps.affiliation.models import Affiliation
from cabbie.apps.account.managers import (
    UserManager, PassengerManager, DriverManager)
from cabbie.common.fields import SeparatedField, JSONField
from cabbie.common.models import (ActiveMixin, NullableImageMixin,
                                  AbstractTimestampModel)
from cabbie.utils.crypt import encrypt
from cabbie.utils.rand import random_string
from cabbie.utils.validator import validate_phone
from cabbie.utils.verify import issue_verification_code, send_verification_code


# Concrete
# --------

def _issue_new_code():
    return random_string(User.CODE_LEN)


class User(AbstractBaseUser, PermissionsMixin, ActiveMixin):
    USERNAME_FIELD = 'phone'  # required by Django
    REQUIRED_FIELDS = []      # required by Django
    CODE_LEN = 6

    phone = models.CharField(u'전화번호', max_length=11, unique=True,
                             validators=[validate_phone])
    name = models.CharField(u'이름', max_length=30)
    is_staff = models.BooleanField(u'관리자', default=False)
    date_joined = models.DateTimeField(u'가입시기', default=timezone.now)

    point = models.PositiveIntegerField(u'포인트', default=0)
    recommend_code = models.CharField(u'추천코드', max_length=10, unique=True,
                                      default=_issue_new_code)
    is_bot = models.BooleanField(u'bot 여부', default=False)
    last_active_at = models.DateTimeField(u'마지막 활동', default=timezone.now)
    bank_account = models.CharField(u'계좌정보', max_length=100, blank=True)

    # Count
    current_month_board_count = models.PositiveIntegerField(u'당월 콜횟수',
                                                            default=0)
    previous_month_board_count = models.PositiveIntegerField(u'전월 콜횟수',
                                                             default=0)
    board_count = models.PositiveIntegerField(u'총 콜횟수', default=0)
    driver_recommend_count = models.PositiveIntegerField(u'추천횟수 (기사)',
                                                         default=0)
    passenger_recommend_count = models.PositiveIntegerField(u'추천횟수 (승객)',
                                                            default=0)
    recommended_count = models.PositiveIntegerField(u'피추천횟수', default=0)

    is_sms_agreed = models.BooleanField(u'SMS 수신동의', default=False)
    is_email_agreed = models.BooleanField(u'이메일 수신동의', default=False)

    # Push
    push_id = models.CharField(u'푸시아이디', max_length=30, default='')

    # App version
    app_version = models.CharField(u'앱버전', max_length=10, default='')

    objects = UserManager()

    class Meta:
        ordering = ['-date_joined']
        verbose_name = u'사용자'
        verbose_name_plural = u'사용자'

    def __unicode__(self):
        if self.is_staff:
            return u'{name} 관리자 ({phone})'.format(name=self.name, phone=self.phone)
        return u'{name}({phone})'.format(name=self.name,
                                           phone=self.phone)

    @property
    def concrete(self):
        for role_name in ('passenger', 'driver'):
            role = self.get_role(role_name)
            if role:
                return role
        return None

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name

    def get_role(self, role_name):
        try:
            return getattr(self, '{0}'.format(role_name))
        except (ObjectDoesNotExist, AttributeError):
            return None

    def has_role(self, role_name):
        return bool(self.get_role(role_name))


class Passenger(User):
    email = models.EmailField(u'이메일', unique=True)
    
    # partnership
    affiliation = models.ForeignKey(Affiliation, related_name='passengers', verbose_name=u'제휴사'
                                    , null=True, blank=True, on_delete=models.SET_NULL)

    objects = PassengerManager()

    class Meta(User.Meta):
        verbose_name = u'승객'
        verbose_name_plural = u'승객'

    def __unicode__(self):
        return u'{name} 승객 ({phone})'.format(name=self.name, phone=self.phone)

    @property
    def is_affiliated(self):
        today = datetime.date.today()

        return self.affiliation is not None \
                and self.affiliation.is_active \
                and self.affiliation.event_start_at <= today and (self.affiliation.event_end_at + datetime.timedelta(days=1)) > today 

    @property
    def is_promotion_applicable(self):
        return ((timezone.now() - self.date_joined).days
                <= settings.PROMOTION_DAYS)

    def dropout(self, dropout_type, note=None):
        PassengerDropout.objects.create(
            user_id=self.id, dropout_type=dropout_type, note=note or '')
        self.delete()

    @property
    def latest_ride(self):
        if self.rides.count() > 0:
            latest = self.rides.latest('created_at')
            return { 
                'id': latest.id, 
                'state': latest.state 
            }
        return None

    # in total
    def _total_ride_count(self):
        from cabbie.apps.drive.models import Ride 

        qs = Ride.objects.filter(passenger=self) 
        qs = qs.filter(Q(state=Ride.BOARDED) | Q(state=Ride.COMPLETED) | Q(state=Ride.RATED))
        
        return len(qs)
    _total_ride_count.short_description = u'총탑승횟수'
    total_ride_count = property(_total_ride_count)



class Driver(NullableImageMixin, User):
    IMAGE_TYPES = ('100s',)

    TAXI_PRIVATE, TAXI_LUXURY = 'private', 'luxury'
    TAXI_TYPES = (
        (TAXI_PRIVATE, u'개인'),
        (TAXI_LUXURY, u'모범'),
    )

    # Authentication
    verification_code = models.CharField(u'인증코드', max_length=10)
    is_verified = models.BooleanField(u'인증여부', default=False)
    is_verification_code_notified = models.BooleanField(u'인증코드 공지여부', default=False)
    is_accepted = models.BooleanField(u'승인여부', default=False)
    is_freezed = models.BooleanField(u'사용제한', default=False)
    freeze_note = models.CharField(u'사용제한 비고', max_length=1000,
                                   blank=True)

    # Meta
    license_number = models.CharField(u'자격증번호', max_length=100,
                                      unique=True)
    car_number = models.CharField(u'차량번호', max_length=20, unique=True)
    car_model = models.CharField(u'차량모델', max_length=50, blank=True)
    company = models.CharField(u'회사', max_length=50)
    max_capacity = models.PositiveIntegerField(u'탑승인원수', default=4)
    garage = models.CharField(u'차고지', max_length=100, blank=True)
    taxi_type = models.CharField(u'택시종류', max_length=10,
                                 choices=TAXI_TYPES)
    taxi_service = SeparatedField(u'서비스', max_length=1000, separator=',',
                                  blank=True,
                                  help_text=u'콤마(,)로 구분하여 여러 개의 '
                                            u'서비스를 입력할 수 있습니다.')
    about = models.CharField(u'소개', max_length=140, blank=True)
    deposit = models.IntegerField(u'예치금', default=0)
    is_super = models.BooleanField(u'우수기사', default=False)
    is_dormant = models.BooleanField(u'휴면기사', default=False)

    is_educated = models.BooleanField(u'교육이수여부', default=False)
    education = models.ForeignKey(Education, related_name='attendees', verbose_name=u'교육', blank=True, null=True, on_delete=models.SET_NULL)

    province = models.CharField(u'시도', max_length=10, default='')
    region = models.CharField(u'지역', max_length=20, default='', blank=True)

    # Rating
    total_ratings_by_category = JSONField(u'총상세평점', default='{}')

    objects = DriverManager()

    class Meta(NullableImageMixin.Meta, User.Meta):
        verbose_name = u'기사'
        verbose_name_plural = u'기사'

    def __unicode__(self):
        return u'{name} 기사 ({phone})'.format(name=self.name, phone=self.phone)

    def get_default_image_url(self, image_type):
        return ''

    @staticmethod
    def get_login_key():
        return encrypt('02-720-2036')

    def send_verification_code(self):
        send_verification_code(self.phone, self.verification_code)

    def freeze(self, is_freezed=True):
        if self.is_freezed == is_freezed:
            return
        self.is_freezed = is_freezed
        self.save(update_fields=['is_freezed'])

    def unfreeze(self):
        self.freeze(False)

    def mark_as_educated(self, education=None):
        if education:
            self.is_educated = True
            self.education = education
        self.save(update_fields=['is_educated', 'education'])

    def mark_as_uneducated(self):
        self.is_educated = False
        self.education = None 
        self.save(update_fields=['is_educated', 'education'])


    def _generate_rating(self):
        _dict = {
            'kindness': [0, 0],
            'cleanliness': [0, 0],
            'security': [0, 0],
        }

        from cabbie.apps.stats.models import DriverRideStatMonth
        from cabbie.apps.drive.models import Ride 

        now = datetime.datetime.now()

        for stat in DriverRideStatMonth.objects.filter(driver=self, year=now.year, month=now.month, state=Ride.RATED):
            for category in _dict.keys(): 
                v, c = stat._ratings_by_category(category)
                _dict[category][0] += v
                _dict[category][1] += c
            
        return _dict 

    def _update_rating(self):
        self.total_ratings_by_category = self._generate_rating()
        self.save(update_fields=['total_ratings_by_category'])

    def _ratings_by_category(self, category):
        return self.total_ratings_by_category.get(category, [0, 0])

    # property : rating (total)
    def _rating(self):

        total_rating = 0
        total_count = 0

        for category in ['kindness', 'cleanliness', 'security']:
            value, count = self._ratings_by_category(category)

            if value and count:
                total_rating += value
                total_count += count 

        return 0.0 if total_rating == 0 and total_count == 0 else float(total_rating) / total_count 

    _rating.short_description = u'종합평점'
    rating = property(_rating)

    # property : rating kindness
    def _rating_kindness(self):
        value, count = self._ratings_by_category('kindness')
        rating = float(value) / count if value and count else 0   # value and count is not None and greater than 0
        rating = '%.3f' % rating

        return u'{rating} ({value}/{count})'.format(rating=rating, value=value, count=count)
    
    _rating_kindness.short_description = u'친절'
    rating_kindness = property(_rating_kindness)

    # property : rating cleanliness
    def _rating_cleanliness(self):
        value, count = self._ratings_by_category('cleanliness')
        rating = float(value) / count if value and count else 0   # value and count is not None and greater than 0
        rating = '%.3f' % rating

        return u'{rating} ({value}/{count})'.format(rating=rating, value=value, count=count)
    
    _rating_cleanliness.short_description = u'청결'
    rating_cleanliness = property(_rating_cleanliness)

    # property : rating security
    def _rating_security(self):
        value, count = self._ratings_by_category('security')
        rating = float(value) / count if value and count else 0   # value and count is not None and greater than 0
        rating = '%.3f' % rating

        return u'{rating} ({value}/{count})'.format(rating=rating, value=value, count=count)
    
    _rating_security.short_description = u'안전'
    rating_security = property(_rating_security)


    @property
    def ratings_by_category(self):
        ret = dict()

        for k, v in self.total_ratings_by_category.iteritems():
            if v[0] > 0 and v[1] > 0:
                ret[k] = float(v[0]) / v[1]
            else:
                ret[k] = 0.0

        return ret

    # current month
    def _rated_count(self):
        total_count = 0

        from cabbie.apps.stats.models import DriverRideStatMonth
        from cabbie.apps.drive.models import Ride 

        now = datetime.datetime.now()

        for stat in DriverRideStatMonth.objects.filter(driver=self, year=now.year, month=now.month, state=Ride.RATED):
            total_count += stat.count
        
        return total_count 
    _rated_count.short_description = u'당월평가횟수'
    rated_count = property(_rated_count)


    # current month
    def _ride_count(self):
        total_count = 0

        from cabbie.apps.stats.models import DriverRideStatMonth
        from cabbie.apps.drive.models import Ride 

        now = datetime.datetime.now()

        for stat in DriverRideStatMonth.objects.filter(driver=self, year=now.year, month=now.month, state=Ride.BOARDED):
            total_count += stat.count
        
        return total_count 
    _ride_count.short_description = u'당월콜횟수'
    ride_count = property(_ride_count)


    # in total
    def _total_rated_count(self):
        total_count = 0

        from cabbie.apps.stats.models import DriverRideStatMonth
        from cabbie.apps.drive.models import Ride 

        for stat in DriverRideStatMonth.objects.filter(driver=self, state=Ride.RATED):
            total_count += stat.count
        
        return total_count 
    _total_rated_count.short_description = u'총평가횟수'
    total_rated_count = property(_total_rated_count)


    # in total
    def _total_ride_count(self):
        total_count = 0

        from cabbie.apps.stats.models import DriverRideStatMonth
        from cabbie.apps.drive.models import Ride 

        for stat in DriverRideStatMonth.objects.filter(driver=self, state=Ride.BOARDED):
            total_count += stat.count
        
        return total_count 
    _total_ride_count.short_description = u'총콜횟수'
    total_ride_count = property(_total_ride_count)


    def profile_image_link(self):
        return '<a href="%s" target="_blank">사진보기</a>' % (self.url,) if self.image else ''
    profile_image_link.allow_tags = True
    profile_image_link.short_description = u'프로필사진'


    def clear_image(self):
        self.image = ''
        self.image_key = ''
        self.image_width = None
        self.image_height = None
        self.save(update_fields=['image', 'image_key', 'image_width', 'image_height'])

    def dropout(self, dropout_type, note=None):
        DriverDropout.objects.create(
            user_id=self.id, dropout_type=dropout_type, note=note or '')
        self.delete()

    @property
    def latest_ride(self):
        if self.rides.count() > 0:
            latest = self.rides.latest('created_at')
            return { 
                'id': latest.id, 
                'state': latest.state 
            }
        return None


    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.verification_code:
            self.verification_code = issue_verification_code()
            if update_fields is not None:
                update_fields.append('verification_code')
        self.set_password(Driver.get_login_key())
        super(Driver, self).save(
            force_insert, force_update, using, update_fields)


class DriverReservation(NullableImageMixin, AbstractTimestampModel):
    IMAGE_TYPES = ('original',)

    phone = models.CharField(u'전화번호', max_length=11, unique=True,
                             validators=[validate_phone])
    name = models.CharField(u'이름', max_length=30)
    car_model = models.CharField(u'차량모델', max_length=50, blank=True, default=u'')
    is_joined = models.BooleanField(u'가입여부', default=False)

    def cert_image_link(self):
        return '<a href="%s" target="_blank">사진보기</a>' % (self.url,) if self.image else ''
    cert_image_link.allow_tags = True
    cert_image_link.short_description = u'자격증 사진'

    class Meta:
        verbose_name = u'기사 가입신청자'
        verbose_name_plural = u'기사 가입신청자'

    def join(self, is_joined=True):
        if self.is_joined:
            return
        self.is_joined = is_joined
        self.save(update_fields=['is_joined'])


class Dropout(AbstractTimestampModel):
    user_id = models.PositiveIntegerField()
    note = models.CharField(u'비고', max_length=1000, blank=True)


class PassengerDropout(Dropout):
    ADMIN, REQUEST = 'admin', 'request'
    DROPOUT_TYPES = (
        (ADMIN, u'운영자 수동'),
        (REQUEST, u'탈퇴 요청'),
    )

    dropout_type = models.CharField(u'탈퇴사유', max_length=10,
                                    choices=DROPOUT_TYPES)

    class Meta(Dropout.Meta):
        verbose_name = u'승객 탈퇴자'
        verbose_name_plural = u'승객 탈퇴자'


class DriverDropout(Dropout):
    ADMIN, REQUEST = 'admin', 'request'
    DROPOUT_TYPES = (
        (ADMIN, u'운영자 수동'),
        (REQUEST, u'탈퇴 요청'),
    )

    dropout_type = models.CharField(u'탈퇴사유', max_length=10,
                                    choices=DROPOUT_TYPES)

    class Meta(Dropout.Meta):
        verbose_name = u'기사 탈퇴자'
        verbose_name_plural = u'기사 탈퇴자'


from cabbie.apps.account.receivers import *
