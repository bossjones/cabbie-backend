# encoding: utf8

from django.contrib import admin
from django import forms

from cabbie.apps.stats.models import (
    DriverRideStatMonth, DriverRideStatWeek, DriverRideStatDay)
from cabbie.common.admin import AbstractAdmin



def rating_round_off(obj):
    return '%.3f' % (round(obj.rating, 3))
rating_round_off.short_description = u'평점'

class DriverRideStatMonthAdmin(AbstractAdmin):
    addable = False
    deletable = False
    ordering = ('-driver', '-year', '-month', 'state')
    list_display = ('driver', 'year', 'month', 'state_kor', 
                    'count_without_admin', rating_round_off, 
                    'rating_value_kindness', 'rating_count_kindness',
                    'rating_value_cleanliness', 'rating_count_cleanliness',
                    'rating_value_security', 'rating_count_security',
                    )
    list_filter = ('driver', 'year', 'month', 'state')

    search_fields = (
        'driver__phone',
        'driver__name',
    )


class DriverRideStatWeekAdmin(AbstractAdmin):
    addable = False
    deletable = False
    ordering = ('-driver', '-year', '-month', '-week', 'state')
    list_display = ('driver', 'year', 'month', 'week', 'state_kor', 
                    'count_without_admin', rating_round_off,
                    'rating_value_kindness', 'rating_count_kindness',
                    'rating_value_cleanliness', 'rating_count_cleanliness',
                    'rating_value_security', 'rating_count_security',
                    )
    list_filter = ('driver', 'year', 'month', 'week', 'state')

    search_fields = (
        'driver__phone',
        'driver__name',
    )


class DriverRideStatDayAdmin(AbstractAdmin):
    addable = False
    deletable = False
    ordering = ('-driver', '-year', '-month', '-week', '-day', 'state')
    list_display = ('driver', 'year', 'month', 'week', 'day', 'state_kor', 
                    'count_without_admin', rating_round_off,
                    'rating_value_kindness', 'rating_count_kindness',
                    'rating_value_cleanliness', 'rating_count_cleanliness',
                    'rating_value_security', 'rating_count_security',
                    )
    list_filter = ('driver', 'year', 'month', 'week', 'day', 'state')

    search_fields = (
        'driver__phone',
        'driver__name',
    )

admin.site.register(DriverRideStatMonth, DriverRideStatMonthAdmin)
admin.site.register(DriverRideStatWeek, DriverRideStatWeekAdmin)
admin.site.register(DriverRideStatDay, DriverRideStatDayAdmin)
