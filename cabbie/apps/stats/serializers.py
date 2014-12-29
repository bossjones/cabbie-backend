from rest_framework import serializers

from cabbie.apps.stats.models import DriverRideStatMonth, DriverRideStatWeek, DriverRideStatDay
from cabbie.common.serializers import AbstractSerializer


class DriverRideStatMonthSerializer(AbstractSerializer):
    count = serializers.Field(source='count')
    rating = serializers.Field(source='rating')

    class Meta:
        model = DriverRideStatMonth
        fields = ('id', 'year', 'month', 'state', 'count', 'rating',
                  'created_at', 'updated_at')

class DriverRideStatWeekSerializer(AbstractSerializer):
    count = serializers.Field(source='count')
    rating = serializers.Field(source='rating')

    class Meta:
        model = DriverRideStatWeek
        fields = ('id', 'year', 'month', 'week', 'state', 'count', 'rating',
                  'created_at', 'updated_at')

class DriverRideStatDaySerializer(AbstractSerializer):
    count = serializers.Field(source='count')
    rating = serializers.Field(source='rating')

    class Meta:
        model = DriverRideStatDay
        fields = ('id', 'year', 'month', 'week', 'day', 'state', 'count', 'rating',
                  'created_at', 'updated_at')
