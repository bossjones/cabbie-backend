# encoding: utf8

from django.db import models

from tinymce import models as tinymce_models
from cabbie.common.models import (ActiveMixin, NullableImageMixin,
                                  AbstractTimestampModel)

class Notice(ActiveMixin, AbstractTimestampModel):
    title = models.CharField(u'제목', max_length=50)
    content = tinymce_models.HTMLField(u'내용', blank=True)
    visible_from = models.DateTimeField(u'게시시간') 

    class Meta(ActiveMixin.Meta, AbstractTimestampModel.Meta):
        verbose_name = u'공지사항'
        verbose_name_plural = u'공지사항'
       
class AppPopup(ActiveMixin, NullableImageMixin, AbstractTimestampModel): 
    title = models.CharField(u'제목', max_length=50)
    content = tinymce_models.HTMLField(u'내용', blank=True)
    link = models.URLField(u'상세링크', max_length=200)
    starts_at= models.DateTimeField(u'시작시간', null=True, db_index=True)
    ends_at = models.DateTimeField(u'종료시간', null=True, db_index=True)

    class Meta(ActiveMixin.Meta, NullableImageMixin.Meta, AbstractTimestampModel.Meta):
        verbose_name = u'앱팝업'
        verbose_name_plural = u'앱팝업'
