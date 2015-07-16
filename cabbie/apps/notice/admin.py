# encoding: utf8
from django.contrib import admin

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

    list_display = ('id', 'title', 'image_preview', 'starts_at', 'ends_at', 'is_active')
    search_fields = (
        'title',
    )
    fields = (
        'id', 'title', 'image', 
        'starts_at', 'ends_at',
        'is_active',
    )
    readonly_fields = (
        'id',
    ) 

    def image_preview(self, obj):
        return u'<a href="{url}"><img src="{url}" width=200></a>'.format(url=obj.url)
    image_preview.short_description = u'미리보기'
    image_preview.allow_tags = True

admin.site.register(AppPopup, AppPopupAdmin)
