# encoding: utf8
import datetime

from django.contrib import admin
from django.contrib.admin.helpers import ActionForm
from django.conf import settings
from django.db.models import Count, Q
from django import forms

from cabbie.apps.account.models import Passenger
from cabbie.apps.drive.models import Request, Ride
from cabbie.apps.kpi.models import PassengerKpiModel
from cabbie.common.admin import AbstractAdmin, DateRangeFilter


class KpiGenerateDateRangeFilter(DateRangeFilter):
    def __init__(self, *args, **kwargs):
        super(KpiGenerateDateRangeFilter, self).__init__(*args, **kwargs)

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
            data['subscriber'] = subscriber

            # active_user
            _filter.clear()
            if not start_filter or start_filter < launch_date:
                start_filter = launch_date

            if start_filter:
                _filter['created_at__gte'] = start_filter

            if end_filter:
                _filter['created_at__lte'] = end_filter

            request_qs = Request.objects_with_tz_normalizer.astimezone('created_at').filter(**_filter)
            active_user = request_qs.distinct('passenger').count()
            data['active_user'] = active_user 

            # requested
            data['ride_requested'] = request_qs.count()

            # approved
            data['ride_approved'] = request_qs.filter(state=Request.APPROVED).count()

            ride_qs = Ride.objects_with_tz_normalizer.astimezone('created_at').filter(**_filter)

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

            PassengerKpiModel.objects.all().delete()
            PassengerKpiModel.objects.create(**data) 
        
            qs = PassengerKpiModel.objects.all()

            return qs 

        else:
            return None
        


class PassengerKpiAdmin(AbstractAdmin):
    addable = False
    deletable = False
    list_display = (
                    'subscriber', 'active_user',
                    '_ride_requested', '_ride_approved', 
                    '_ride_canceled', '_ride_rejected',
                    '_ride_completed', '_complete_rate', '_ride_rated', '_rated_ratio', '_average_rate', '_satisfied_ratio',
                    )

    list_filter = (
        ('start_filter', KpiGenerateDateRangeFilter),
    )

    def __init__(self, *args, **kwargs):
        super(PassengerKpiAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = (None, )

    def _ride_requested(self, obj):
        return obj.ride_requested
    _ride_requested.short_description = u'콜요청(A)'

    def _ride_approved(self, obj):
        return obj.ride_approved
    _ride_approved.short_description = u'수락'

    def _ride_canceled(self, obj):
        return obj.ride_canceled
    _ride_canceled.short_description = u'승객취소'

    def _ride_rejected(self, obj):
        return obj.ride_rejected
    _ride_rejected.short_description = u'기사거절'

    def _ride_completed(self, obj):
        return obj.ride_completed
    _ride_completed.short_description = u'운행완료(B)'

    def _complete_rate(self, obj):
        return "%.1f" % (100.0 * obj.ride_completed / obj.ride_requested if obj.ride_requested > 0 else 0.0) 
    _complete_rate.short_description = u'운행완료율(B/A)(%)'

    def _ride_rated(self, obj):
        return obj.ride_rated
    _ride_rated.short_description = u'평가완료(C)'
     
    def _rated_ratio(self, obj):
        return "%.1f" % (100.0 * obj.ride_rated / obj.ride_completed if obj.ride_completed > 0 else 0.0) 
    _rated_ratio.short_description = u'평가완료율(C/B)(%)'

    def _average_rate(self, obj):
        return "%.1f" % (1.0 * obj.ride_rate_sum / obj.ride_rated / 3 if obj.ride_rated > 0 else 0.0)
    _average_rate.short_description = u'평균평점'

    def _satisfied_ratio(self, obj):
        return "%.1f" % (100.0 * obj.ride_satisfied / obj.ride_rated if obj.ride_rated > 0 else 0.0)
    _satisfied_ratio.short_description = u'4.5이상 비율(%)'

admin.site.register(PassengerKpiModel, PassengerKpiAdmin)
