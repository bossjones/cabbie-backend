from cabbie.apps.drive.models import Ride
from cabbie.common.serializers import AbstractSerializer


class RideSerializer(AbstractSerializer):
    class Meta:
        model = Ride
        fields = ('id', 'passenger', 'driver', 'state')
