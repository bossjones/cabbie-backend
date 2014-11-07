from cabbie.apps.account.serializers import (
    DriverSerializer, PassengerSerializer)
from cabbie.apps.drive.models import Ride, Favorite
from cabbie.common.serializers import AbstractSerializer, JSONField, PointField


class RideSerializer(AbstractSerializer):
    passenger = PassengerSerializer(read_only=True)
    driver = DriverSerializer(read_only=True)
    source = JSONField(source='source')
    destination = JSONField(source='destination')
    summary = JSONField(source='summary')
    ratings_by_category = JSONField(source='ratings_by_category')

    class Meta:
        model = Ride
        fields = ('id', 'passenger', 'driver', 'state', 'reason', 'source',
                  'destination', 'summary', 'rating', 'ratings_by_category',
                  'comment', 'created_at', 'updated_at')


class FavoriteSerializer(AbstractSerializer):
    location = PointField(source='location')

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'location', 'address', 'poi', 'created_at')
