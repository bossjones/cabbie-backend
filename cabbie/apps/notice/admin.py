# encoding: utf8

from django import forms

from django.contrib import admin
from django.utils import timezone
from django.contrib.admin.widgets import AdminTextareaWidget

from cabbie.apps.notice.models import Notice, AppPopup
from cabbie.common.admin import AbstractAdmin

class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        widgets = {
            'content': AdminTextareaWidget(),
        }

class NoticeAdmin(AbstractAdmin):
    form = NoticeForm

    list_display = ('id', 'title', 'image_preview', 'notice_type', 'visibility', 'link', 'visible_from', 'created_at')
    search_fields = (
        'content',
    )
    list_filter = ('notice_type',)
    fields = ('id', 'title', 'notice_type', 'visibility', 'image', 'content', 'link', 'link_label', 'visible_from', 'new_until', 'is_active',)
    readonly_fields = (
        'id',
    ) 

    def image_preview(self, obj):
        return u'<a href="{url}"><img src="{url}" width=200></a>'.format(url=obj.url)
    image_preview.short_description = u'미리보기'
    image_preview.allow_tags = True


class AppPopupAdmin(AbstractAdmin):
    list_display = ('id', 'title', 'image_preview', 'link', 'starts_at', 'ends_at', 'status')
    search_fields = (
        'title',
    )
    fields = (
        'id', 'title', 'image', 'link', 
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
admin.site.register(Notice, NoticeAdmin)
