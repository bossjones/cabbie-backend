# encoding: utf8

from django.contrib import admin
from django import forms

from cabbie.apps.policy.models import (
    LocationDataAccess, LocationDataProvide,
    LocationDataNotice)
from cabbie.common.admin import AbstractAdmin


class LocationDataAccessAdmin(AbstractAdmin):
    list_display = ('user', 'created_at_', 'updated_at_')

    def created_at_(self, obj):
        return obj.created_at

    def updated_at_(self, obj):
        return obj.updated_at

    created_at_.short_description = u'로그인'
    updated_at_.short_description = u'로그아웃'


class LocationDataProvideAdmin(AbstractAdmin):
    list_display = ('provider', 'provider_type', 'service','providee',
                    'created_at_')

    def created_at_(self, obj):
        return obj.created_at

    created_at_.short_description = u'제공시간'


class LocationDataNoticeAdmin(AbstractAdmin):
    list_display = ('noticer', 'requester', 'purpose',
                    'created_at_', 'updated_at_')

    def created_at_(self, obj):
        return obj.created_at

    def updated_at_(self, obj):
        return obj.updated_at

    created_at_.short_description = u'요청시간'
    updated_at_.short_description = u'고지시간'

admin.site.register(LocationDataAccess, LocationDataAccessAdmin)
admin.site.register(LocationDataProvide, LocationDataProvideAdmin)
admin.site.register(LocationDataNotice, LocationDataNoticeAdmin)
