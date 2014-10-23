# encoding: utf8

import datetime

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from cabbie.apps.account.managers import (
    UserManager, PassengerManager, DriverManager)
from cabbie.common.fields import SeparatedField
from cabbie.common.models import ActiveMixin, NullableImageMixin, TimestampMixin
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

    phone = models.CharField(_('phone'), max_length=11, unique=True,
                             validators=[validate_phone])
    name = models.CharField(_('name'), max_length=30)
    is_staff = models.BooleanField(_('staff status'), default=False)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    point = models.PositiveIntegerField(default=0)
    recommend_code = models.CharField(max_length=10, unique=True,
                                      default=_issue_new_code)
    is_bot = models.BooleanField(default=False)

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

    @property
    def get_remain_days_for_promotion(self):
        return (self.date_joined
                + datetime.timedelta(days=settings.PROMOTION_DAYS)
                - timezone.now()).days

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
    email = models.EmailField(_('email address'), unique=True)
    ride_count = models.PositiveIntegerField(_('ride count'), default=0)

    objects = PassengerManager()

    class Meta(User.Meta):
        verbose_name = u'승객'
        verbose_name_plural = u'승객'

    @property
    def is_promotion_applicable(self):
        return ((timezone.now() - self.date_joined).days
                <= settings.PROMOTION_DAYS)


class Driver(NullableImageMixin, User):
    IMAGE_TYPES = ('100s',)

    TAXI_PRIVATE, TAXI_LUXURY = 'private', 'luxury'
    TAXI_TYPES = (
        (TAXI_PRIVATE, u'개인'),
        (TAXI_LUXURY, u'모범'),
    )

    verification_code = models.CharField(max_length=10)
    is_verified = models.BooleanField(default=False)
    is_accepted = models.BooleanField(default=False)
    is_freezed = models.BooleanField(default=False)

    license_number = models.CharField(_('license number'), max_length=100,
                                      unique=True)
    car_number = models.CharField(_('car number'), max_length=20, unique=True)
    car_model = models.CharField(_('car model'), max_length=50)
    company = models.CharField(_('company'), max_length=50)
    bank_account = models.CharField(_('bank account'), max_length=100)
    max_capacity = models.PositiveIntegerField(_('max capacity'), default=4)
    taxi_type = models.CharField(max_length=10, choices=TAXI_TYPES)
    taxi_service = SeparatedField(max_length=1000, separator=',', blank=True)
    about = models.CharField(max_length=140, blank=True)

    total_rating = models.PositiveIntegerField(_('total rating'), default=0)

    rated_count = models.PositiveIntegerField(_('rated count'), default=0)
    ride_count = models.PositiveIntegerField(_('ride count'), default=0)
    deposit = models.IntegerField(_('deposit'), default=0)

    objects = DriverManager()

    class Meta(NullableImageMixin.Meta, User.Meta):
        verbose_name = u'기사'
        verbose_name_plural = u'기사'

    @property
    def rating(self):
        return (float(self.total_rating) / self.rated_count
                if self.rated_count > 0 else None)

    def get_default_image_url(self, image_type):
        return ''

    def get_login_key(self):
        return encrypt(self.verification_code)

    def send_verification_code(self):
        send_verification_code(self.phone, self.verification_code)

    def freeze(self, is_freezed=True):
        if self.is_freezed:
            return
        self.is_freezed = is_freezed
        self.save(update_fields=['is_freezed'])

    def unfreeze(self):
        self.freeze(False)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.verification_code:
            self.verification_code = issue_verification_code()
            if update_fields is not None:
                update_fields.append('verification_code')
        self.set_password(self.get_login_key())
        super(Driver, self).save(
            force_insert, force_update, using, update_fields)

class DriverReservation(TimestampMixin):
    phone = models.CharField(_('phone'), max_length=11, unique=True,
                             validators=[validate_phone])
    name = models.CharField(_('name'), max_length=30)
    is_joined = models.BooleanField(default=False)

    class Meta:
        verbose_name = u'기사 가입신청자'
        verbose_name_plural = u'기사 가입신청자'

    def join(self, is_joined=True):
        if self.is_joined:
            return
        self.is_joined = is_joined
        self.save(update_fields=['is_joined'])


from cabbie.apps.account.receivers import *
