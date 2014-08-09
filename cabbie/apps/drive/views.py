from django.contrib.gis.geos import Point
from django.http import Http404
from rest_framework import viewsets

from cabbie.apps.drive.models import Ride
from cabbie.apps.drive.serializers import RideSerializer
from cabbie.common.views import InternalView
from cabbie.utils import json


# REST
# ----

class RideViewSet(viewsets.ModelViewSet):
    queryset = Ride.objects.prefetch_related('passenger', 'driver').all()
    serializer_class = RideSerializer

    # FIXME: Permission control

    def get_queryset(self):
        return self.queryset.filter(passenger__user=self.request.user)


# Internal
# --------

class InternalRideCreateView(InternalView):
    def post(self, request):
        data = json.loads(request.body)

        ride = Ride.objects.create(
            passenger_id=data['passenger_id'],
            driver_id=data['driver_id'],
            state=data['state'],
            source=Point(*data['passenger_location'])
        )

        ride.histories.create(
            driver=ride.driver,
            state=ride.state,
            passenger_location=Point(*data['passenger_location']),
            driver_location=Point(*data['driver_location']),
            data=data,
        )

        return self.render_json({'id': ride.id})


class InternalRideUpdateView(InternalView):
    def _get_ride(self, pk):
        try:
            return Ride.objects.get(pk=pk)
        except Ride.DoesNotExist:
            raise Http404

    def post(self, request, pk=None):
        data = json.loads(request.body)
        ride = self._get_ride(pk)
        ride.transit(**data)
        return self.render_json()
