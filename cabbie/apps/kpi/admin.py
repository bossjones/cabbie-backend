# encoding: utf8
import datetime

from django.contrib import admin
from django.contrib.admin.helpers import ActionForm
from django.conf import settings
from django.db.models import Count, Q
from django import forms

from cabbie.apps.account.models import Passenger, Driver
from cabbie.apps.drive.models import Province, Region, Request, Ride
from cabbie.apps.kpi.models import PassengerKpiModel, DriverKpiModel
from cabbie.common.admin import AbstractAdmin, DateRangeFilter


def _process_kpi(request_qs, ride_qs, place, place_label, lookup_field):
    data = {}

    place_request_qs = request_qs.filter(**{lookup_field:place})
    
    active_user = place_request_qs.distinct('passenger').count()
    data['active_user'] = active_user 

    data[place_label] = place.name

    if isinstance(place, Region):
        data['province'] = place.province
        
    # by distance
    total = place_request_qs.count()
    data['ride_short'] = place_request_qs.filter(distance__range=(0, 3000)).count() / total if total > 0 else 0
    data['ride_medium'] = place_request_qs.filter(distance__range=(3000, 6000)).count() / total if total > 0 else 0
    data['ride_long'] = place_request_qs.filter(distance__range=(6000, 10000)).count() / total if total > 0 else 0
    data['ride_xlong'] = place_request_qs.filter(distance__gte=10000).count() / total if total > 0 else 0

    # requested
    data['ride_requested'] = place_request_qs.count()

    # approved
    data['ride_approved'] = place_request_qs.filter(state=Request.APPROVED).count()

    lookup = { 'approved_request__{0}'.format(lookup_field): place }

    place_ride_qs = ride_qs.filter(**lookup)

    # canceled
    data['ride_canceled'] = place_ride_qs.filter(state=Ride.CANCELED).count()

    # rejected
    data['ride_rejected'] = place_ride_qs.filter(state=Ride.REJECTED).count()

    # completed
    data['ride_completed'] = place_ride_qs.filter(Q(state=Ride.BOARDED) | Q(state=Ride.COMPLETED) | Q(state=Ride.RATED)).count()

    # rated
    ride_qs_rated = place_ride_qs.filter(state=Ride.RATED)
    data['ride_rated'] = ride_qs_rated.count()

    # rate_point, satisfied
    ride_rate_sum = 0
    satisfied = 0
    for ride in ride_qs_rated:
        total = ride.rating_kindness + ride.rating_cleanliness + ride.rating_security 
        ride_rate_sum += total
        satisfied += 1 if float(total) / 3.0 >= 4.5 else 0

    data['ride_rate_sum'] = ride_rate_sum
    data['ride_satisfied'] = satisfied 

    return data



class PassengerKpiGenerateDateRangeFilter(DateRangeFilter):
    def __init__(self, *args, **kwargs):
        super(PassengerKpiGenerateDateRangeFilter, self).__init__(*args, **kwargs)

    def queryset(self, request, queryset):
        if self.form.is_valid():
            # get no null params
            filter_params = dict(filter(lambda x: bool(x[1]),
                                self.form.cleaned_data.items()))

            # range
            start_filter = filter_params.get('{0}__gte'.format(self.field_path))
            end_filter = filter_params.get('{0}__lte'.format(self.field_path))
            if end_filter:
                end_filter = end_filter + datetime.timedelta(days=1)

            # launch_date
            launch_date = datetime.datetime.strptime(settings.BKTAXI_GRAND_LAUNCH_DATE, "%Y-%m-%d").date()

            # generate
            data = {}
            if start_filter:
                data['start_filter'] = start_filter

            if end_filter:
                data['end_filter'] = end_filter 
            
            # subscriber
            _filter = {}
            if start_filter:
                _filter['date_joined__gte'] = start_filter

            if end_filter:
                _filter['date_joined__lte'] = end_filter

            subscriber = Passenger.objects.astimezone('date_joined').filter(**_filter).count() 

            _filter.clear()
            if not start_filter or start_filter < launch_date:
                start_filter = launch_date

            if start_filter:
                _filter['created_at__gte'] = start_filter

            if end_filter:
                _filter['created_at__lte'] = end_filter

            request_qs = Request.objects_with_tz_normalizer.astimezone('created_at').filter(**_filter)
            ride_qs = Ride.objects_with_tz_normalizer.astimezone('created_at').filter(**_filter)

            PassengerKpiModel.objects.all().delete()

            # Per province
            # ------------
            provinces = Province.objects.all()

            for province in provinces:            
                
                data = _process_kpi(request_qs, ride_qs, province, 'province', 'source_province')

                PassengerKpiModel.objects.create(**data) 
            
                # Per region
                # ----------
                regions = Region.objects.filter(province=province, depth=1)

                for region in regions:
                    data = _process_kpi(request_qs, ride_qs, region, 'region', 'source_region1')

                    PassengerKpiModel.objects.create(**data) 
    


            # Total    
            # -----
            data['subscriber'] = subscriber

            active_user = request_qs.distinct('passenger').count()
            data['active_user'] = active_user 

            data['province'] = 'Total' 

            # requested
            data['ride_requested'] = request_qs.count()

            # approved
            data['ride_approved'] = request_qs.filter(state=Request.APPROVED).count()

            # canceled
            data['ride_canceled'] = ride_qs.filter(state=Ride.CANCELED).count()

            # rejected
            data['ride_rejected'] = ride_qs.filter(state=Ride.REJECTED).count()

            # completed
            data['ride_completed'] = ride_qs.filter(Q(state=Ride.BOARDED) | Q(state=Ride.COMPLETED) | Q(state=Ride.RATED)).count()

            # rated
            ride_qs_rated = ride_qs.filter(state=Ride.RATED)
            data['ride_rated'] = ride_qs_rated.count()

            # rate_point, satisfied
            ride_rate_sum = 0
            satisfied = 0
            for ride in ride_qs_rated:
                total = ride.rating_kindness + ride.rating_cleanliness + ride.rating_security 
                ride_rate_sum += total
                satisfied += 1 if float(total) / 3.0 >= 4.5 else 0

            data['ride_rate_sum'] = ride_rate_sum
            data['ride_satisfied'] = satisfied 

            PassengerKpiModel.objects.create(**data) 


            qs = PassengerKpiModel.objects.all()

            return qs 

        else:
            return None
        

class PassengerKpiAdmin(AbstractAdmin):
    list_max_show_all = 1000
    list_per_page = 300

    addable = False
    deletable = False
    list_display = (
                    'subscriber', 
                    '_dynamic_province',
                    'region',
                    'active_user', 
                    '_ride_requested', '_ride_approved', '_approval_rate',
                    '_ride_canceled', '_cancel_rate', 
                    '_ride_rejected', '_reject_rate',
                    '_ride_completed', '_complete_rate', '_ride_rated', '_rated_ratio', '_average_rate', '_satisfied_ratio',
                    )

    list_filter = (
        ('start_filter', PassengerKpiGenerateDateRangeFilter),
        'province',
    )

    def _dynamic_province(self, obj):
        return '' if obj.region else obj.province 
    _dynamic_province.short_description= u'시도'

    def __init__(self, *args, **kwargs):
        super(PassengerKpiAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = (None, )

    def _ride_requested(self, obj):
        return obj.ride_requested
    _ride_requested.short_description = u'콜요청(A)'

    def _ride_approved(self, obj):
        return obj.ride_approved
    _ride_approved.short_description = u'수락(B)'

    def _approval_rate(self, obj):
        return "%.1f" % (100.0 * obj.ride_approved / obj.ride_requested if obj.ride_requested > 0 else 0.0)
    _approval_rate.short_description = u'수락율(B/A)(%)'

    def _ride_canceled(self, obj):
        return obj.ride_canceled
    _ride_canceled.short_description = u'승객취소(C)'

    def _cancel_rate(self, obj):
        return "%.1f" % (100.0 * obj.ride_canceled / obj.ride_approved if obj.ride_approved > 0 else 0.0)
    _cancel_rate.short_description = u'승객취소율(C/B)(%)'

    def _ride_rejected(self, obj):
        return obj.ride_rejected
    _ride_rejected.short_description = u'기사거절(D)'

    def _reject_rate(self, obj):
        return "%.1f" % (100.0 * obj.ride_rejected / obj.ride_approved if obj.ride_approved > 0 else 0.0)
    _reject_rate.short_description = u'기사거절율(D/B)(%)'

    def _ride_completed(self, obj):
        return obj.ride_completed
    _ride_completed.short_description = u'운행완료(E)'

    def _complete_rate(self, obj):
        return "%.1f" % (100.0 * obj.ride_completed / obj.ride_requested if obj.ride_requested > 0 else 0.0) 
    _complete_rate.short_description = u'운행완료율(E/A)(%)'

    def _ride_rated(self, obj):
        return obj.ride_rated
    _ride_rated.short_description = u'평가완료(F)'
     
    def _rated_ratio(self, obj):
        return "%.1f" % (100.0 * obj.ride_rated / obj.ride_completed if obj.ride_completed > 0 else 0.0) 
    _rated_ratio.short_description = u'평가완료율(F/E)(%)'

    def _average_rate(self, obj):
        return "%.2f" % (1.0 * obj.ride_rate_sum / obj.ride_rated / 3 if obj.ride_rated > 0 else 0.0)
    _average_rate.short_description = u'평균평점'

    def _satisfied_ratio(self, obj):
        return "%.1f" % (100.0 * obj.ride_satisfied / obj.ride_rated if obj.ride_rated > 0 else 0.0)
    _satisfied_ratio.short_description = u'4.5이상 비율(%)'


# Driver
class DriverKpiGenerateDateRangeFilter(DateRangeFilter):
    def __init__(self, *args, **kwargs):
        super(DriverKpiGenerateDateRangeFilter, self).__init__(*args, **kwargs)

    def queryset(self, request, queryset):
        if self.form.is_valid():
            # get no null params
            filter_params = dict(filter(lambda x: bool(x[1]),
                                self.form.cleaned_data.items()))

            # range
            start_filter = filter_params.get('{0}__gte'.format(self.field_path))
            end_filter = filter_params.get('{0}__lte'.format(self.field_path))
            if end_filter:
                end_filter = end_filter + datetime.timedelta(days=1)

            # launch_date
            launch_date = datetime.datetime.strptime(settings.BKTAXI_GRAND_LAUNCH_DATE, "%Y-%m-%d").date()

            # generate
            data = {}
            if start_filter:
                data['start_filter'] = start_filter

            if end_filter:
                data['end_filter'] = end_filter 
            
            # subscriber
            _filter = {}
            if start_filter:
                _filter['date_joined__gte'] = start_filter

            if end_filter:
                _filter['date_joined__lte'] = end_filter

            subscriber = Driver.objects.astimezone('date_joined').filter(**_filter).count() 
            data['subscriber'] = subscriber

            # active_user
            _filter.clear()
            if not start_filter or start_filter < launch_date:
                start_filter = launch_date

            if start_filter:
                _filter['created_at__gte'] = start_filter

            if end_filter:
                _filter['created_at__lte'] = end_filter

            _filter['state'] = Ride.RATED

            ride_qs = Ride.objects_with_tz_normalizer.astimezone('created_at').filter(**_filter)

            rate_sum_of_educated, rate_count_of_educated = 0,0
            rate_sum_of_uneducated, rate_count_of_uneducated = 0,0

            for ride in ride_qs:
                total = ride.rating_kindness + ride.rating_cleanliness + ride.rating_security 

                if ride.is_educated_driver():
                    rate_sum_of_educated += total
                    rate_count_of_educated += 1
                else:
                    rate_sum_of_uneducated += total
                    rate_count_of_uneducated += 1
            
            data['rate_sum_of_educated'] = rate_sum_of_educated
            data['rate_count_of_educated'] = rate_count_of_educated
                    
            data['rate_sum_of_uneducated'] = rate_sum_of_uneducated
            data['rate_count_of_uneducated'] = rate_count_of_uneducated

            DriverKpiModel.objects.all().delete()
            DriverKpiModel.objects.create(**data) 
        
            qs = DriverKpiModel.objects.all()

            return qs 

        else:
            return None
        

class DriverKpiAdmin(AbstractAdmin):
    addable = False
    deletable = False
    list_display = (
                    'subscriber', '_average_rate_of_educated', '_average_rate_of_uneducated',
                    )

    list_filter = (
        ('start_filter', DriverKpiGenerateDateRangeFilter),
    )

    def _average_rate_of_educated(self, obj):
        return "%.2f" % (1.0 * obj.rate_sum_of_educated / obj.rate_count_of_educated / 3 if obj.rate_count_of_educated else 0.0) 
    _average_rate_of_educated.short_description = u'정규교육 이수 기사 평균평점'

    def _average_rate_of_uneducated(self, obj):
        return "%.2f" % (1.0 * obj.rate_sum_of_uneducated / obj.rate_count_of_uneducated / 3 if obj.rate_count_of_uneducated else 0.0) 
    _average_rate_of_uneducated.short_description = u'교육 비이수 기사 평균평점'

    def __init__(self, *args, **kwargs):
        super(DriverKpiAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = (None, )


admin.site.register(PassengerKpiModel, PassengerKpiAdmin)
admin.site.register(DriverKpiModel, DriverKpiAdmin)
