# encoding: utf8

import datetime

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import F
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from cabbie.apps.account.managers import (
    UserManager, PassengerManager, DriverManager)
from cabbie.common.fields import SeparatedField
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
    bank_account = models.CharField(u'계좌정보', max_length=100)

    # Count
    current_month_board_count = models.PositiveIntegerField(u'당월 콜횟수',
                                                            default=0)
    previous_month_board_count = models.PositiveIntegerField(u'전월 콜횟수',
                                                             default=0)
    board_count = models.PositiveIntegerField(u'총 콜횟수', default=0)
    ride_count = models.PositiveIntegerField(u'총 배차횟수', default=0)

    objects = UserManager()

    class Meta:
        ordering = ['-date_joined']
        verbose_name = u'사용자'
        verbose_name_plural = u'사용자'

    def __unicode__(self):
        if self.is_staff:
            return u'{name} 관리자'.format(name=self.name)
        elif self.get_role('passenger'):
            return u'{name} 승객'.format(name=self.name)
        elif self.get_role('driver'):
            return u'{name} 기사'.format(name=self.name)
        return u'{class_}({phone})'.format(class_=self.__class__.__name__,
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

    objects = PassengerManager()

    class Meta(User.Meta):
        verbose_name = u'승객'
        verbose_name_plural = u'승객'

    @property
    def is_promotion_applicable(self):
        return ((timezone.now() - self.date_joined).days
                <= settings.PROMOTION_DAYS)

    def dropout(self, dropout_type, note=None):
        PassengerDropout.objects.create(
            user_id=self.id, dropout_type=dropout_type, note=note or '')
        self.delete()


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
    is_accepted = models.BooleanField(u'승인여부', default=False)
    is_freezed = models.BooleanField(u'사용제한', default=False)
    freeze_note = models.CharField(u'사용제한 비고', max_length=1000,
                                   blank=True)

    # Meta
    license_number = models.CharField(u'자격증번호', max_length=100,
                                      unique=True)
    car_number = models.CharField(u'차량번호', max_length=20, unique=True)
    car_model = models.CharField(u'차량모델', max_length=50)
    company = models.CharField(u'회사', max_length=50)
    max_capacity = models.PositiveIntegerField(u'탑승인원수', default=4)
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

    # Rating
    total_rating = models.PositiveIntegerField(u'총평점', default=0)
    rated_count = models.PositiveIntegerField(u'평가횟수', default=0)
    rating = models.FloatField(u'평점', default=0.0)

    objects = DriverManager()

    class Meta(NullableImageMixin.Meta, User.Meta):
        verbose_name = u'기사'
        verbose_name_plural = u'기사'

    def get_default_image_url(self, image_type):
        return ''

    def get_login_key(self):
        return encrypt(self.verification_code)

    def send_verification_code(self):
        send_verification_code(self.phone, self.verification_code)

    def freeze(self, is_freezed=True):
        if self.is_freezed == is_freezed:
            return
        self.is_freezed = is_freezed
        self.save(update_fields=['is_freezed'])

    def unfreeze(self):
        self.freeze(False)

    def rate(self, rating):
        self.rated_count = F('rated_count') + 1
        self.total_rating = F('total_rating') + rating
        self.rating = float(self.total_rating) / self.rated_count
        self.save(update_fields=['rated_count', 'total_rating', 'rating'])

    def dropout(self, dropout_type, note=None):
        DriverDropout.objects.create(
            user_id=self.id, dropout_type=dropout_type, note=note or '')
        self.delete()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.verification_code:
            self.verification_code = issue_verification_code()
            if update_fields is not None:
                update_fields.append('verification_code')
        self.set_password(self.get_login_key())
        super(Driver, self).save(
            force_insert, force_update, using, update_fields)


class DriverReservation(AbstractTimestampModel):
    phone = models.CharField(u'전화번호', max_length=11, unique=True,
                             validators=[validate_phone])
    name = models.CharField(u'이름', max_length=30)
    is_joined = models.BooleanField(u'가입여부', default=False)

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
