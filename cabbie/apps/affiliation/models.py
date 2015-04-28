# encoding: utf8

from django.conf import settings
from django.db import models
from cabbie.common.models import ActiveMixin, NullableImageMixin, AbstractTimestampModel


class Affiliation(NullableImageMixin, ActiveMixin, AbstractTimestampModel):
    IMAGE_TYPES = ('original', '100s')  
    CODE_LEN = 6

    name = models.CharField(u'이름', max_length=30)
    certificate_code = models.CharField(u'인증코드', unique=True, max_length=20)
    ride_mileage = models.PositiveIntegerField(u'탑승마일리지', blank=True
                                            , default=settings.POINTS_BY_TYPE['ride_point_for_the_affiliated'])

    class Meta(NullableImageMixin.Meta, ActiveMixin.Meta, AbstractTimestampModel.Meta):
        verbose_name = u'제휴사'
        verbose_name_plural = u'제휴사'

from cabbie.apps.affiliation.receivers import *
