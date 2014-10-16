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
    provider = models.ForeignKey(User, related_name='location_data_provider_history',
                                verbose_name=u'제공한자')
    provider_type = models.CharField(max_length=20, verbose_name=u'취득경로')
    service = models.CharField(max_length=20, verbose_name=u'제공서비스')
    providee = models.ForeignKey(User, related_name='location_data_providee_history', blank=True,
                                verbose_name=u'제공받은자')

    class Meta(AbstractTimestampModel.Meta):
        verbose_name = u'위치정보 이용제공내역'
        verbose_name_plural = u'위치정보 이용제공내역'

class LocationDataNotice(AbstractTimestampModel):
    noticer = models.ForeignKey(User, related_name='location_data_noticer_history',
                                        verbose_name=u'취급자')
    requester = models.ForeignKey(User, related_name='location_data_requester_history',
                                        verbose_name=u'요청자')
    purpose = models.CharField(max_length=100, verbose_name=u'목적')
    
    class Meta(AbstractTimestampModel.Meta):
        verbose_name = u'위치정보 열람및고지내역'
        verbose_name_plural = u'위치정보 열람및고지내역'
