# encoding: utf8
from django.contrib import admin
from django.utils import timezone

from cabbie.apps.notice.models import Notice, AppPopup
from cabbie.common.admin import AbstractAdmin

class NoticeAdmin(AbstractAdmin):
    change_form_template = 'notice/admin/change_form.html'

    list_display = ('id', 'title', 'visible_from', 'created_at')
    search_fields = (
        'content',
    )
    fields = ('id', 'title', 'content', 'visible_from', 'is_active',)
    readonly_fields = (
        'id',
    ) 

class AppPopupAdmin(AbstractAdmin):
    change_form_template = 'notice/admin/change_form.html'

    list_display = ('id', 'title', 'image_preview', 'starts_at', 'ends_at', 'status')
    search_fields = (
        'title',
    )
    fields = (
        'id', 'title', 'image', 
        'starts_at', 'ends_at',
    )
    readonly_fields = (
        'id',
    ) 

    def image_preview(self, obj):
        return u'<a href="{url}"><img src="{url}" width=200></a>'.format(url=obj.url)
    image_preview.short_description = u'미리보기'
    image_preview.allow_tags = True

    def status(self, obj):
        now = timezone.now()
        if now < obj.starts_at:
            return u'게시전'
        if now >= obj.starts_at and now < obj.ends_at:
            return u'게시중' 
        else:
            return u'종료'
    status.short_description = u'상태'
        


admin.site.register(AppPopup, AppPopupAdmin)
