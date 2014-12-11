from cabbie.apps.stats.models import DriverRideStatMonth, DriverRideStatWeek, DriverRideStatDay
from cabbie.common.serializers import AbstractSerializer


class DriverRideStatMonthSerializer(AbstractSerializer):
    class Meta:
        model = DriverRideStatMonth
        fields = ('id', 'year', 'month', 'state', 'count', 'ratings',
                  'created_at', 'updated_at')

class DriverRideStatWeekSerializer(AbstractSerializer):
    class Meta:
        model = DriverRideStatWeek
        fields = ('id', 'year', 'month', 'week', 'state', 'count', 'ratings',
                  'created_at', 'updated_at')

class DriverRideStatDaySerializer(AbstractSerializer):
    class Meta:
        model = DriverRideStatDay
        fields = ('id', 'year', 'month', 'week', 'day', 'state', 'count', 'ratings',
                  'created_at', 'updated_at')
