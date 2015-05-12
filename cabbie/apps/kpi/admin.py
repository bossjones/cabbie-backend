# encoding: utf8
import datetime

from django.contrib import admin
from django.contrib.admin.helpers import ActionForm
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

            # satisfied
            satisfied = 0
            for ride in ride_qs_rated:
                total = ride.rating_kindness + ride.rating_cleanliness + ride.rating_security 
                satisfied += 1 if float(total) / 3.0 >= 4.5 else 0

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
                    'ride_requested', 'ride_approved', 'approval_rate',
                    'ride_canceled', 'ride_rejected',
                    'ride_completed', 'ride_rated', 'ride_satisfied',
                    )

    list_filter = (
        ('start_filter', KpiGenerateDateRangeFilter),
    )

    def __init__(self, *args, **kwargs):
        super(PassengerKpiAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = (None, )

    def approval_rate(self, obj):
        return "%.1f" % (100.0 * obj.ride_approved / obj.ride_requested if obj.ride_requested > 0 else 0.0) 

admin.site.register(PassengerKpiModel, PassengerKpiAdmin)
