from django.conf import settings
from django.contrib.gis.geos import Point
from django.http import Http404
from rest_framework import status
from rest_framework import viewsets

from cabbie.apps.drive.models import Ride, Favorite
from cabbie.apps.drive.serializers import RideSerializer, FavoriteSerializer
from cabbie.common.views import InternalView, APIView
from cabbie.utils import json
from cabbie.utils.geo import TMap, TMapError


# REST
# ----

class RideViewSet(viewsets.ModelViewSet):
    queryset = Ride.objects.prefetch_related('passenger', 'driver').all()
    serializer_class = RideSerializer
    filter_fields = ('state', 'passenger', 'driver', 'created_at',
                     'updated_at')
    ordering = ('-created_at',)

    def get_queryset(self):
        user = self.request.user
        qs = self.queryset
        if user.has_role('passenger'):
            qs = qs.filter(passenger=user)
        elif user.has_role('driver'):
            qs = qs.filter(driver=user)
        return qs


class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.prefetch_related('passenger').all()
    serializer_class = FavoriteSerializer
    filter_fields = ()
    ordering = ('-created_at',)

    def pre_save(self, obj):
        obj.passenger = self.request.user.get_role('passenger')

    def get_queryset(self):
        return self.queryset.filter(passenger=self.request.user)


class GeoPOIView(APIView):
    def get(self, request, *args, **kwargs):
        data = request.GET
        try:
            q = data['q'].strip()
            location = (data['location'].split(',') if 'location' in data else
                        None)
        except KeyError as e:
            return self.render_error(
                unicode(e), code='ERR_INVALID_PARAMETER',
                status=status.HTTP_400_BAD_REQUEST)

        try:
            result = TMap().poi_search(
                q, location=location, page=data.get('page', 1),
                count=data.get('count', settings.DEFAULT_PAGE_SIZE))
        except TMapError as e:
            return self.render_error(
                unicode(e), code='ERR_TMAP_ERROR',
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return self.render(result)


class GeoPOIAroundView(APIView):
    def get(self, request, *args, **kwargs):
        data = request.GET
        try:
            location = data['location'].split(',')
        except KeyError as e:
            return self.render_error(
                unicode(e), code='ERR_INVALID_PARAMETER',
                status=status.HTTP_400_BAD_REQUEST)

        try:
            result = TMap().poi_search_around(
                location, page=data.get('page', 1),
                count=data.get('count', settings.DEFAULT_PAGE_SIZE))
        except TMapError as e:
            return self.render_error(
                unicode(e), code='ERR_TMAP_ERROR',
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return self.render(result)


class GeoReverseView(APIView):
    def get(self, request, *args, **kwargs):
        data = request.GET
        try:
            location = data['location'].split(',')
        except KeyError as e:
            return self.render_error(
                unicode(e), code='ERR_INVALID_PARAMETER',
                status=status.HTTP_400_BAD_REQUEST)

        try:
            result = TMap().reverse_geocoding(location)
        except TMapError as e:
            return self.render_error(
                unicode(e), code='ERR_TMAP_ERROR',
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return self.render({
                'address': result
            })


# Internal
# --------

class InternalRideCreateView(InternalView):
    def post(self, request):
        data = json.loads(request.body)

        source = data['source']
        destination = data['destination']

        ride = Ride.objects.create(
            passenger_id=data['passenger_id'],
            driver_id=data['driver_id'],
            state=data['state'],
            source=source,
            source_location=Point(*source['location']),
            destination=destination,
            destination_location=Point(*destination['location']),
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
