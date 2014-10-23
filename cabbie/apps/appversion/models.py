# encoding: utf8

from django.db import models
from django.utils.translation import ugettext_lazy as _

from cabbie.common.models import ActiveMixin
# Create your models here.

class AndroidDriver(ActiveMixin):
    version_code = models.PositiveIntegerField(_('version code'))
    version_name = models.CharField(_('version name'), max_length=10, unique=True)
    is_update_required = models.BooleanField(default=False)
    description = models.CharField(_('description'), max_length=500)
    
    class Meta:
        ordering = ['-version_code'] 
        verbose_name = u'안드로이드 기사앱 버전관리'
        verbose_name_plural = u'안드로이드 기사앱 버전관리'
