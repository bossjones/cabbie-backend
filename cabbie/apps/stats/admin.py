# encoding: utf8

from django.contrib import admin
from django import forms

from cabbie.apps.stats.models import (
    DriverRideStatMonth, DriverRideStatWeek, DriverRideStatDay, 
    LocationDataAccess, LocationDataProvide,
    LocationDataNotice)
from cabbie.common.admin import AbstractAdmin


class DriverRideStatMonthAdmin(AbstractAdmin):
    addable = False
    deletable = False
    ordering = ('-driver', '-year', '-month', 'state')
    list_display = ('driver', 'year', 'month', 'state_kor', 'count', 'rating',
                    'updated_at', 'created_at')
    list_filter = ('driver', 'year', 'month', 'state')

class DriverRideStatWeekAdmin(AbstractAdmin):
    addable = False
    deletable = False
    ordering = ('-driver', '-year', '-month', '-week', 'state')
    list_display = ('driver', 'year', 'month', 'week', 'state_kor', 'count', 'rating',
                    'updated_at', 'created_at')
    list_filter = ('driver', 'year', 'month', 'week', 'state')

class DriverRideStatDayAdmin(AbstractAdmin):
    addable = False
    deletable = False
    ordering = ('-driver', '-year', '-month', '-week', '-day', 'state')
    list_display = ('driver', 'year', 'month', 'week', 'day', 'state_kor', 'count', 'rating',
                    'updated_at', 'created_at')
    list_filter = ('driver', 'year', 'month', 'week', 'day', 'state')




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


admin.site.register(DriverRideStatMonth, DriverRideStatMonthAdmin)
admin.site.register(DriverRideStatWeek, DriverRideStatWeekAdmin)
admin.site.register(DriverRideStatDay, DriverRideStatDayAdmin)
admin.site.register(LocationDataAccess, LocationDataAccessAdmin)
admin.site.register(LocationDataProvide, LocationDataProvideAdmin)
admin.site.register(LocationDataNotice, LocationDataNoticeAdmin)
