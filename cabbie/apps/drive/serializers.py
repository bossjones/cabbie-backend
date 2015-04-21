from rest_framework import serializers

from cabbie.apps.account.serializers import (
    DriverSerializer, PassengerSerializer)
from cabbie.apps.drive.models import Request, Ride, Favorite, Hotspot
from cabbie.common.serializers import AbstractSerializer, JSONField, PointField


class RideSerializer(AbstractSerializer):
    passenger = PassengerSerializer(read_only=True)
    driver = DriverSerializer(read_only=True)
    source = JSONField(source='source')
    destination = JSONField(source='destination')
    summary = JSONField(source='summary')
    ratings_by_category = JSONField(source='ratings_by_category')
    rating = serializers.Field(source='rating')

    class Meta:
        model = Ride
        fields = ('id', 'passenger', 'driver', 'state', 'reason', 'source',
                  'destination', 'charge_type', 'summary', 'rating', 'ratings_by_category',
                  'comment', 'created_at', 'updated_at')


class RequestSerializer(AbstractSerializer):
    passenger = PassengerSerializer(read_only=True)
    approval = RideSerializer(read_only=True)
    contacts = JSONField(source='contacts')
    rejects = JSONField(source='rejects')
    approval_driver_json = JSONField(source='approval_driver_json')

    class Meta:
        model = Request
        fields = ('id', 'passenger', 'approval', 'contacts', 'rejects', 'state', 'approval_driver_json')

class FavoriteSerializer(AbstractSerializer):
    location = PointField(source='location')

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'location', 'address', 'poi', 'created_at')


class HotspotSerializer(AbstractSerializer):
    location = PointField(source='location')

    class Meta:
        model = Hotspot
        fields = ('id', 'location', 'address', 'poi', 'ride_count', 'weight',
                  'is_promotion')
