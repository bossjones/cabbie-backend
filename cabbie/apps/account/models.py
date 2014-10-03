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
from cabbie.common.models import ActiveMixin, NullableImageMixin
from cabbie.utils.crypt import encrypt
from cabbie.utils.validator import validate_phone
from cabbie.utils.verify import issue_verification_code, send_verification_code


# Concrete
# --------

class User(AbstractBaseUser, PermissionsMixin, ActiveMixin):
    USERNAME_FIELD = 'phone'  # required by Django
    REQUIRED_FIELDS = []      # required by Django

    phone = models.CharField(_('phone'), max_length=11, unique=True,
                             validators=[validate_phone])
    name = models.CharField(_('name'), max_length=30)
    is_staff = models.BooleanField(_('staff status'), default=False)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    point = models.PositiveIntegerField(default=0)

    objects = UserManager()

    class Meta:
        ordering = ['-date_joined']
        verbose_name = u'사용자'
        verbose_name_plural = u'사용자'

    def __unicode__(self):
        return u'{class_}({phone})'.format(class_=self.__class__.__name__,
                                           phone=self.phone)

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

    verification_code = models.CharField(max_length=10)
    is_verified = models.BooleanField(default=False)
    is_accepted = models.BooleanField(default=False)
    is_freezed = models.BooleanField(default=False)

    license_number = models.CharField(_('license number'), max_length=100,
                                      unique=True)
    car_number = models.CharField(_('car number'), max_length=20, unique=True)
    company = models.CharField(_('company'), max_length=50)
    bank_account = models.CharField(_('bank account'), max_length=100)

    ride_count = models.PositiveIntegerField(_('ride count'), default=0)

    objects = DriverManager()

    class Meta(NullableImageMixin.Meta, User.Meta):
        verbose_name = u'기사'
        verbose_name_plural = u'기사'

    @property
    def rating(self):
        # FIXME: Implement this
        import random
        return random.randint(1, 50) / 10.0

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


from cabbie.apps.account.receivers import *
