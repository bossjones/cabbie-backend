from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from cabbie.apps.account.managers import (
    UserManager, PassengerManager, DriverManager)
from cabbie.common.models import ActiveMixin, AbstractTimestampModel
from cabbie.utils.validator import validate_phone


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

    objects = UserManager()

    class Meta:
        ordering = ['-date_joined']
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __unicode__(self):
        return u'User({phone})'.format(phone=self.phone)

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name

    def get_role(self, role_name):
        try:
            return getattr(self, '{0}'.format(role_name))
        except (ObjectDoesNotExist, AttributeError) as e:
            return None


class Passenger(User):
    email = models.EmailField(_('email address'), unique=True)
    ride_count = models.PositiveIntegerField(_('ride count'), default=0)

    objects = PassengerManager()


class Driver(User):
    licence_number = models.CharField(_('license number'), max_length=100,
                                      unique=True)
    ride_count = models.PositiveIntegerField(_('ride count'), default=0)

    objects = DriverManager()


from cabbie.apps.account.receivers import *
