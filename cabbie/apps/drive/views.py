from rest_framework import viewsets

from cabbie.apps.drive.models import Ride
from cabbie.apps.drive.serializers import RideSerializer


class RideViewSet(viewsets.ModelViewSet):
    queryset = Ride.objects.prefetch_related(
        'passenger__user', 'driver__user').all()
    serializer_class = RideSerializer

    def get_queryset(self):
        return self.queryset.filter(passenger__user=self.request.user)
