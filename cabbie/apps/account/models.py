from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from cabbie.apps.account.managers import UserManager
from cabbie.common.models import ActiveMixin
from cabbie.utils.validator import validate_username


class User(AbstractBaseUser, PermissionsMixin, ActiveMixin):
    USERNAME_FIELD = 'username'    # required by Django
    REQUIRED_FIELDS = ['email']    # required by Django

    username = models.CharField(
        _('username'), max_length=30, unique=True,
        validators=[validate_username])
    email = models.EmailField(_('email address'), unique=True)
    name = models.CharField(_('name'), max_length=30)
    is_staff = models.BooleanField(_('staff status'), default=False)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    class Meta:
        ordering = ['-date_joined']
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __unicode__(self):
        return self.username

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name
