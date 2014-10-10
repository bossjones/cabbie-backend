# encoding: utf8

from django.db import models
from django.utils.translation import ugettext_lazy as _

from cabbie.apps.account.models import User
from cabbie.common.models import AbstractTimestampModel


class LocationDataAccess(AbstractTimestampModel):
    user = models.ForeignKey(User, related_name='location_data_accesses',
                             verbose_name=u'접근한 사용자')

    class Meta(AbstractTimestampModel.Meta):
        verbose_name = u'위치정보 접근로그'
        verbose_name_plural = u'위치정보 접근로그'

class LocationDataProvide(AbstractTimestampModel):
    recipient = models.CharField(max_length=100, verbose_name=u'이용제공처')

    class Meta(AbstractTimestampModel.Meta):
        verbose_name = u'위치정보 이용제공내역'
        verbose_name_plural = u'위치정보 이용제공내역'
