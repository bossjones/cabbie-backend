from cabbie.apps.stats.models import DriverRideStat
from cabbie.common.serializers import AbstractSerializer


class DriverRideStatSerializer(AbstractSerializer):
    class Meta:
        model = DriverRideStat
        fields = ('id', 'year', 'month', 'week', 'state', 'count',
                  'created_at', 'updated_at')
