# encoding: utf8

from django.db import models

from cabbie.common.models import AbstractTimestampModel

class Education(AbstractTimestampModel):
    name = models.CharField(u'교육명', max_length=20)
    place = models.CharField(u'장소', max_length=20)
    started_at = models.DateTimeField(u'교육시간')
    lecturer = models.CharField(u'강사', max_length=20)

    class Meta(AbstractTimestampModel.Meta):
        verbose_name = u'교육'
        verbose_name_plural = u'교육'

    def __unicode__(self):
        return u'{name}'.format(name=self.name)
