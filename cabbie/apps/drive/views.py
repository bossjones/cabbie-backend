from django.conf import settings
from django.db.models import Q
from django.contrib.gis.geos import Point
from django.http import Http404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from cabbie.apps.drive.models import Ride, RideHistory, Favorite, Hotspot
from cabbie.apps.drive.serializers import (
    RideSerializer, FavoriteSerializer, HotspotSerializer)
from cabbie.apps.drive.receivers import post_ride_requested
from cabbie.apps.stats.models import DriverRideStatWeek
from cabbie.common.views import InternalView, APIView, APIMixin
from cabbie.utils import json
from cabbie.utils.geo import TMap, TMapError
from cabbie.utils.date import week_of_month


# REST
# ----

class RideViewSet(APIMixin, viewsets.ModelViewSet):
    queryset = Ride.objects.prefetch_related('passenger', 'driver').all()
    serializer_class = RideSerializer
    filter_fields = ('state', 'passenger', 'driver', 'created_at',
                     'updated_at')
    ordering = ('-created_at',)

    def get_queryset(self):
        user = self.request.user
        qs = self.queryset

        if user.is_superuser:
            return qs

        if user.has_role('passenger'):
            qs = qs.filter(passenger=user)
        elif user.has_role('driver'):
            qs = qs.filter(driver=user)

        # state : boarded OR completed
        valid = self.request.QUERY_PARAMS.get('valid', None)
        if valid:
            qs = qs.filter(Q(state='boarded') | Q(state='completed') | Q(state='rated'))

        # year 
        year = self.request.QUERY_PARAMS.get('year', None)
        if year:
            qs = qs.filter(created_at__year=year)

        # month
        month = self.request.QUERY_PARAMS.get('month', None)
        if month:
            qs = qs.filter(created_at__month=month)

        # week
        week = self.request.QUERY_PARAMS.get('week', None)
        if week:
            ride_ids = []
            for stat_week in DriverRideStatWeek.objects.filter(year=year, month=month, week=week).all(): 
                ride_ids.extend(stat_week.rides)
            qs = qs.filter(id__in=ride_ids)

        return qs

    @action(methods=['PUT'])
    def rate(self, request, pk=None):
        ride = self.get_object()
        try:
            ride.rate(request.DATA['ratings_by_category'],
                      request.DATA['comment'])
        except Exception as e:
            return self.render_error(unicode(e))
        return self.render()


class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.prefetch_related('passenger').all()
    serializer_class = FavoriteSerializer
    filter_fields = ('address',)
    ordering = ('-created_at',)

    def pre_save(self, obj):
        obj.passenger = self.request.user.get_role('passenger')

    def get_queryset(self):
        return self.queryset.filter(passenger=self.request.user)


class HotspotViewSet(APIMixin, viewsets.ModelViewSet):
    queryset = Hotspot.objects.all().order_by('-weight')
    serializer_class = HotspotSerializer
    filter_fields = ('created_at', 'updated_at', 'is_promotion')
    ordering = ('-weight',)


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

        data['state'] = 'requested'

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
            charge_type=data['charge_type'],
            additional_message=data['additional_message'],
        )

        if ride.state == Ride.REQUESTED:
            post_ride_requested.send(sender=Ride, ride=ride)

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

class InternalRideFetchView(InternalView):
    def _get_ride(self, pk):
        try:
            return RideHistory.objects.filter(ride__id=pk).latest('updated_at')
        except Ride.DoesNotExist:
            raise Http404

    def post(self, request, pk=None):
        ride = self._get_ride(pk)
        return self.render_json({'state': ride.state})
