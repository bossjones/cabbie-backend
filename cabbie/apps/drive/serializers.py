from cabbie.apps.account.serializers import DriverSerializer, PassengerSerializer
from cabbie.apps.drive.models import Ride
from cabbie.common.serializers import AbstractSerializer, JSONField, PointField


class RideSerializer(AbstractSerializer):
    passenger = PassengerSerializer(read_only=True)
    driver = DriverSerializer(read_only=True)
    source = JSONField(source='source')
    destination = JSONField(source='destination')

    class Meta:
        model = Ride
        fields = ('id', 'passenger', 'driver', 'state', 'source',
                  'destination', 'created_at', 'updated_at')
