from django.core.exceptions import PermissionDenied
from rest_framework import viewsets

from cabbie.apps.stats.models import DriverRideStatMonth, DriverRideStatWeek, DriverRideStatDay
from cabbie.apps.stats.serializers import DriverRideStatMonthSerializer, DriverRideStatWeekSerializer, DriverRideStatDaySerializer
from cabbie.common.views import APIMixin


class DriverRideStatMonthViewSet(APIMixin, viewsets.ModelViewSet):
    queryset = DriverRideStatMonth.objects.prefetch_related('driver').all()
    serializer_class = DriverRideStatMonthSerializer
    filter_fields = ('year', 'month', 'state', 'created_at',
                     'updated_at')
    ordering = ('-created_at',)

    def get_queryset(self):
        user = self.request.user
        qs = self.queryset

        if user.has_role('driver'):
            return qs.filter(driver=user)

        raise PermissionDenied

class DriverRideStatWeekViewSet(APIMixin, viewsets.ModelViewSet):
    queryset = DriverRideStatWeek.objects.prefetch_related('driver').all()
    serializer_class = DriverRideStatWeekSerializer
    filter_fields = ('year', 'month', 'week', 'state', 'created_at',
                     'updated_at')
    ordering = ('-created_at',)

    def get_queryset(self):
        user = self.request.user
        qs = self.queryset

        if user.has_role('driver'):
            return qs.filter(driver=user)

        raise PermissionDenied

class DriverRideStatDayViewSet(APIMixin, viewsets.ModelViewSet):
    queryset = DriverRideStatDay.objects.prefetch_related('driver').all()
    serializer_class = DriverRideStatDaySerializer
    filter_fields = ('year', 'month', 'week', 'day', 'state', 'created_at',
                     'updated_at')
    ordering = ('-created_at',)

    def get_queryset(self):
        user = self.request.user
        qs = self.queryset

        if user.has_role('driver'):
            return qs.filter(driver=user)

        raise PermissionDenied
