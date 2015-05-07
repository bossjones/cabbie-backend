# encoding: utf8

from django.conf import settings
from django.db import models
from django.utils import timezone
from cabbie.common.models import ActiveMixin, NullableImageMixin, AbstractTimestampModel


class Affiliation(NullableImageMixin, ActiveMixin, AbstractTimestampModel):
    IMAGE_TYPES = ('original', '100s')  
    CODE_LEN = 6

    name = models.CharField(u'이름', max_length=30)
    company_code = models.CharField(u'회사코드', max_length=10)
    affiliated_at = models.DateField(u'제휴일자', default=timezone.now)
    certificate_code = models.CharField(u'인증코드', unique=True, max_length=20)
    ride_mileage = models.PositiveIntegerField(u'탑승마일리지', blank=True
                                            , default=settings.POINTS_BY_TYPE['ride_point_for_the_affiliated'])

    event_start_at = models.DateField(u'이벤트 시작일자', default=timezone.now)
    event_end_at = models.DateField(u'이벤트 종료일자', default=timezone.now)

    class Meta(NullableImageMixin.Meta, ActiveMixin.Meta, AbstractTimestampModel.Meta):
        verbose_name = u'제휴사'
        verbose_name_plural = u'제휴사'

    def __unicode__(self):
        return u'{name}'.format(name=self.name)

from cabbie.apps.affiliation.receivers import *
