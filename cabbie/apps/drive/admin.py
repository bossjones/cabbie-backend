# encoding: utf8

from django import forms
from django.contrib import admin
from django.db.models import Q

from cabbie.apps.drive.models import Request, Ride, RideHistory, Favorite, Hotspot
from cabbie.common.admin import AbstractAdmin, DateRangeFilter
from cabbie.common.widgets import PointWidget


def rating_round_off(obj):
    return "%.3f" % (obj.rating)
rating_round_off.short_description = u'평점'

class RequestAdmin(AbstractAdmin):
    list_filter = ('passenger', 'created_at') 
    search_fields = ('=id', 'passenger__name', 'passenger__phone', '=passenger__email')
    ordering = ('-created_at',)
    list_display = ('id', 'passenger', 'source_information', 'destination_information', 'distance_in_kilometer', 
            'state', 'contacts', 'description_for_contacts_by_distance', 'rejects', 'link_to_ride', 'approved_driver', 'updated_at', 'created_at')

    def approved_driver(self, obj):
        return obj.approval.driver if obj.approval else None
    approved_driver.short_description = u'승인기사'

    def distance_in_kilometer(self, obj):
        return "%.1fkm" % (float(obj.distance) / 1000)
    distance_in_kilometer.short_description = u'요청거리'


    def link_to_ride(self, obj):
        if obj.approval:
            url = u'/admin/drive/ride/?id={0}'.format(obj.approval.id)
            return u'<a href="{0}">{1}</a>'.format(url, obj.approval.id)
        return None
    link_to_ride.short_description = u'승인된 배차'
    link_to_ride.allow_tags = True


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
        'rollback_to_rejected',
        'rollback_to_canceled',
    )

    def rollback_to_rejected(self, request, queryset):
        rides = list(queryset.all())
        for ride in rides:
            # if already rejected, ignore
            if ride.state == Ride.REJECTED:
                continue

            # if rated, reset
            if ride.state == Ride.RATED:
                ride.state = Ride.REJECTED
                ride.ratings_by_category = '{}'
                ride.comment = ''
                ride.save(update_fields=['state', 'ratings_by_category', 'comment'])

            # remove boarded, completed state if any
            ride.histories.filter(Q(state=Ride.BOARDED) | Q(state=Ride.COMPLETED)).delete()

            # transit to rejected state
            data = ride.histories.latest('id').data
            data.update({'state': Ride.REJECTED, 'admin': True })
            ride.transit(**data)
    rollback_to_rejected.short_description = u'기사취소처리'


    def rollback_to_canceled(self, request, queryset):
        rides = list(queryset.all())
        for ride in rides:
            # if already canceled, ignore
            if ride.state == Ride.CANCELED:
                continue

            # if rated, reset
            if ride.state == Ride.RATED:
                ride.state = Ride.CANCELED
                ride.ratings_by_category = '{}'
                ride.comment = ''
                ride.save(update_fields=['state', 'ratings_by_category', 'comment'])

            # remove boarded, completed state if any
            ride.histories.filter(Q(state=Ride.BOARDED) | Q(state=Ride.COMPLETED)).delete()

            # transit to canceled state
            data = ride.histories.latest('id').data
            data.update({'state': Ride.CANCELED, 'admin': True })
            ride.transit(**data)
    rollback_to_canceled.short_description = u'승객취소처리'


    def transit_to_completed(self, request, queryset):
        rides = list(queryset.all())
        for ride in rides:
            transit_states = None
            if ride.state == Ride.BOARDED:
                transit_states = [Ride.COMPLETED]

            elif ride.state == Ride.REQUESTED:
                transit_states = [Ride.APPROVED, Ride.BOARDED, Ride.COMPLETED]

            elif ride.state == Ride.APPROVED:
                transit_states = [Ride.BOARDED, Ride.COMPLETED]

            elif ride.state == Ride.ARRIVED:
                transit_states = [Ride.BOARDED, Ride.COMPLETED]

            elif ride.state == Ride.REJECTED:
                transit_states = [Ride.APPROVED, Ride.BOARDED, Ride.COMPLETED]

            elif ride.state == Ride.CANCELED:
                transit_states = [Ride.APPROVED, Ride.BOARDED, Ride.COMPLETED]

            elif ride.state == Ride.DISCONNECTED:
                transit_states = [Ride.APPROVED, Ride.BOARDED, Ride.COMPLETED]

            elif ride.state == Ride.RATED:
                transit_states = [Ride.APPROVED, Ride.BOARDED, Ride.COMPLETED]
            

            if transit_states:
                data = ride.histories.latest('id').data
                
                for state in transit_states:
                    data.update({'state': state, 'admin': True })
                    if len(ride.histories.filter(state=state).all()) == 0:
                        ride.transit(**data)
    transit_to_completed.short_description = u'운행완료처리'
        
class RideHistoryAdmin(AbstractAdmin):
    addable = False
    deletable = True 
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


admin.site.register(Request, RequestAdmin)
admin.site.register(Ride, RideAdmin)
admin.site.register(RideHistory, RideHistoryAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Hotspot, HotspotAdmin)
