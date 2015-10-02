# encoding: utf8

from django.db import models
from django.utils import timezone

from tinymce import models as tinymce_models
from cabbie.common.models import (ActiveMixin, NullableImageMixin,
                                  AbstractTimestampModel)

class Notice(ActiveMixin, NullableImageMixin, AbstractTimestampModel):
    TYPE_EVENT, TYPE_UPDATE, TYPE_NEWS = 'event', 'update', 'news'
    NOTICE_TYPES = (
        (TYPE_EVENT,    u'이벤트'),
        (TYPE_UPDATE,   u'업데이트'),
        (TYPE_NEWS,     u'백기사 뉴스'),
    )

    VISIBILITY_ALL, VISIBILITY_DRIVER, VISIBILITY_PASSENGER = 'visibility_all', 'visibility_driver', 'visibility_passenger'
    NOTICE_VISIBILITIES = (
        (VISIBILITY_ALL,        u'전체'),
        (VISIBILITY_DRIVER,     u'기사'),
        (VISIBILITY_PASSENGER,  u'승객'),
    ) 

    title = models.CharField(u'제목', max_length=50)
    content = tinymce_models.HTMLField(u'내용', blank=True)
    notice_type = models.CharField(u'타입', max_length=10, choices=NOTICE_TYPES, default=TYPE_EVENT)
    link = models.URLField(u'상세링크', max_length=200, blank=True, null=True)
    link_label = models.CharField(u'상세링크 버튼명', max_length=15, default=u'자세히 보기', blank=True, null=True)
    visible_from = models.DateTimeField(u'게시시간') 
    visibility = models.CharField(u'타겟', max_length=30, choices=NOTICE_VISIBILITIES, default=VISIBILITY_ALL)
    new_until = models.DateTimeField(u'NEW 표시 마감시간')

    class Meta(ActiveMixin.Meta, AbstractTimestampModel.Meta):
        verbose_name = u'공지사항'
        verbose_name_plural = u'공지사항'

    @property
    def is_new(self):
        now = timezone.now()
        return now >= self.visible_from and now < self.new_until
       
class AppPopup(ActiveMixin, NullableImageMixin, AbstractTimestampModel): 
    title = models.CharField(u'제목', max_length=50)
    content = tinymce_models.HTMLField(u'내용', blank=True)
    link = models.URLField(u'상세링크', max_length=200, blank=True, null=True)
    starts_at= models.DateTimeField(u'시작시간', null=True, db_index=True)
    ends_at = models.DateTimeField(u'종료시간', null=True, db_index=True)

    class Meta(ActiveMixin.Meta, NullableImageMixin.Meta, AbstractTimestampModel.Meta):
        verbose_name = u'앱팝업'
        verbose_name_plural = u'앱팝업'
