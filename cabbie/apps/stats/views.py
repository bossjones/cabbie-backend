from django.core.exceptions import PermissionDenied
from rest_framework import viewsets

from cabbie.apps.stats.models import DriverRideStat
from cabbie.apps.stats.serializers import DriverRideStatSerializer
from cabbie.common.views import APIMixin


class DriverRideStatViewSet(APIMixin, viewsets.ModelViewSet):
    queryset = DriverRideStat.objects.prefetch_related('driver').all()
    serializer_class = DriverRideStatSerializer
    filter_fields = ('year', 'month', 'week', 'state', 'created_at',
                     'updated_at')
    ordering = ('-created_at',)

    def get_queryset(self):
        user = self.request.user
        qs = self.queryset

        if user.has_role('driver'):
            return qs.filter(driver=user)

        raise PermissionDenied
