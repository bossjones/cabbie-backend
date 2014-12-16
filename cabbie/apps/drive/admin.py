# encoding: utf8

from django import forms
from django.contrib import admin

from cabbie.apps.drive.models import Ride, RideHistory, Favorite, Hotspot
from cabbie.common.admin import AbstractAdmin, DateRangeFilter
from cabbie.common.widgets import PointWidget


class RideAdmin(AbstractAdmin):
    list_filter = ('state', 'updated_at', 'created_at')
    search_fields = (
        '=id',
        'passenger__name',
        '^passenger__phone',
        '=passenger__email',
        'driver__name',
        '^driver__phone',
    )
    ordering = ('-updated_at',) 
    list_display = ('id', 'passenger', 'driver', 'state_kor', 'source_address',
                    'source_poi', 'destination_address', 'destination_poi',
                    'rating', 'comment', 'updated_at', 'created_at')
    readonly_fields = (
        'passenger', 'driver', 'state_kor', 'source', 'source_location',
        'destination', 'destination_location', 'rating', 'ratings_by_category',
        'comment', 'charge_type', 'summary', 'updated_at', 'created_at',
    )


class RideHistoryAdmin(AbstractAdmin):
    list_display = ('id', 'ride', 'driver', 'state', 'passenger_location',
                    'driver_location', 'created_at')


class FavoriteAdmin(AbstractAdmin):
    list_filter = ('created_at',)
    list_display = ('id', 'passenger', 'name', 'location', 'address', 'poi',
                    'created_at')
    search_fields = ('address', 'poi', 'name')


class HotspotForm(forms.ModelForm):
    class Meta:
        model = Hotspot
        widgets = {
            'location': PointWidget({'rows': 2}),
        }


class HotspotAdmin(AbstractAdmin):
    ordering = ('-weight',)
    form = HotspotForm
    list_filter = ('is_promotion', 'created_at')
    list_display = ('location', 'address', 'poi', 'is_promotion',
                    'ride_count', 'weight', 'created_at')
    fieldsets = (
        (None, {
            'fields': (
                'location', 'address', 'poi', 'is_promotion', 'weight',
            ),
        }),
        ('읽기전용', {'fields': ('ride_count', 'created_at')}),
    )
    readonly_fields = ('ride_count', 'created_at')
    search_fields = ('address', 'poi')


admin.site.register(Ride, RideAdmin)
admin.site.register(RideHistory, RideHistoryAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Hotspot, HotspotAdmin)
