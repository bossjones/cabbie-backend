# encoding: utf8

from django import forms
from django.contrib import admin

from cabbie.apps.drive.models import Ride, RideHistory, Favorite, Hotspot
from cabbie.common.admin import AbstractAdmin, DateRangeFilter
from cabbie.common.widgets import PointWidget


def rating_round_off(obj):
    return "%.3f" % (obj.rating)
rating_round_off.short_description = u'평점'

class RideAdmin(AbstractAdmin):
    deletable = True 

    list_max_show_all = 1000
     
    list_filter = ('driver', 'passenger', 'state', 'updated_at', 'created_at')
    search_fields = (
        '=id',
        'passenger__name',
        'passenger__phone',
        '=passenger__email',
        'driver__name',
        'driver__phone',
    )
    ordering = ('-updated_at',) 
    list_display = ('id', 'driver', 'passenger', 'state_kor', 'reason_kor', 'source_address',
                    'source_poi', 'destination_address', 'destination_poi',
                    rating_round_off, 'rating_kindness', 'rating_cleanliness', 'rating_security', 'comment', 'updated_at', 'created_at')

    fieldsets = (
        (None, { 
            'fields': (
                'state',
            ),
        }),
        ('읽기전용', {'fields': ('driver', 'passenger', 'updated_at', 'created_at')}),
    )

    readonly_fields = (
        'passenger', 'driver', 'state_kor', 'source', 'source_location',
        'destination', 'destination_location', rating_round_off, 'ratings_by_category',
        'comment', 'charge_type', 'summary', 'updated_at', 'created_at',
    )

    actions = (
        'transit_to_completed',
    )

    def transit_to_completed(self, request, queryset):
        rides = list(queryset.all())
        for ride in rides:
            transit_states = None
            if ride.state == 'boarded':
                transit_states = ['completed']

            elif ride.state == 'requested':
                transit_states = ['approved', 'boarded', 'completed']

            elif ride.state == 'approved':
                transit_states = ['boarded', 'completed']

            elif ride.state == 'arrived':
                transit_states = ['boarded', 'completed']

            elif ride.state == 'rejected':
                transit_states = ['approved', 'boarded', 'completed']

            elif ride.state == 'canceled':
                transit_states = ['approved', 'boarded', 'completed']

            elif ride.state == 'disconnected':
                transit_states = ['approved', 'boarded', 'completed']

            elif ride.state == 'rated':
                transit_states = ['approved', 'boarded', 'completed']
            

            if transit_states:
                data = ride.histories.latest('id').data
                
                for state in transit_states:
                    data.update({'state': state, 'admin': True })
                    if len(ride.histories.filter(state=state).all()) == 0:
                        ride.transit(**data)
    transit_to_completed.short_description = u'운행완료처리'
        
class RideHistoryAdmin(AbstractAdmin):
    addable = False
    deletable = False
    search_fields = (
        '=ride__id',
        'driver__name',
        'driver__phone',
    )
    list_filter = ('driver', 'state',)
    list_display = ('ride', 'driver', 'passenger', 'state_kor', 'reject_reason', 'admin', 'passenger_location',
                    'driver_location', 'updated_at', 'created_at')

    def passenger(self, obj):
        return obj.ride.passenger

    def state_kor(self, obj):
        return Ride.STATE_EXPRESSION.get(obj.state, '')

    def reject_reason(self, obj):
        return Ride.REASON_EXPRESSION.get(obj.ride.reason, '') if obj.state == Ride.REJECTED else ''

    def admin(self, obj):
        if obj.is_admin:
            return u'어드민'
        else:
            return ''

class FavoriteAdmin(AbstractAdmin):
    addable = False
    deletable = False
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
