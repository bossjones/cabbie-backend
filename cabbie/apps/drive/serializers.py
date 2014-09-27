from cabbie.apps.account.serializers import (
    DriverSerializer, PassengerSerializer)
from cabbie.apps.drive.models import Ride
from cabbie.common.serializers import AbstractSerializer, JSONField


class RideSerializer(AbstractSerializer):
    passenger = PassengerSerializer(read_only=True)
    driver = DriverSerializer(read_only=True)
    source = JSONField(source='source')
    destination = JSONField(source='destination')
    summary = JSONField(source='summary')
    ratings_by_category = JSONField(source='ratings_by_category')

    class Meta:
        model = Ride
        fields = ('id', 'passenger', 'driver', 'state', 'source',
                  'destination', 'summary', 'rating', 'ratings_by_category',
                  'comment', 'created_at', 'updated_at')
