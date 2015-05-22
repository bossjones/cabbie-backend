# encoding: utf8
from django.contrib import admin

from cabbie.apps.notice.models import Notice, AppPopup
from cabbie.common.admin import AbstractAdmin

class NoticeAdmin(AbstractAdmin):
    list_display = ('id', 'title', 'visible_from', 'created_at')
    search_fields = (
        'content',
    )
    fields = ('id', 'title', 'content', 'visible_from', 'is_active',)
    readonly_fields = (
        'id',
    ) 

class AppPopupAdmin(AbstractAdmin):
    list_display = ('id', 'title', 'content', 'link', 'starts_at', 'ends_at', 'is_active')
    search_fields = (
        'title',
        'content',
    )
    fields = (
        'id', 'title', 'content', 'image', 'link', 
        'starts_at', 'ends_at',
        'is_active',
    )
    readonly_fields = (
        'id',
    ) 


admin.site.register(Notice, NoticeAdmin)
admin.site.register(AppPopup, AppPopupAdmin)
