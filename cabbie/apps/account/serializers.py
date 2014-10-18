from rest_framework import serializers
from rest_framework.authtoken.serializers import (
    AuthTokenSerializer as BaseAuthTokenSerializer)

from cabbie.apps.account.models import User, Passenger, Driver
from cabbie.common.serializers import AbstractSerializer, SeparatedField


class AuthTokenSerializer(BaseAuthTokenSerializer):
    def validate(self, attrs):
        attrs = super(AuthTokenSerializer, self).validate(attrs)

        driver = attrs['user'].get_role('driver')
        if driver:
            if not driver.is_verified:
                raise serializers.ValidationError(u'Must be verified first')
            if not driver.is_accepted:
                raise serializers.ValidationError(u'Must be accepted first')
            if driver.is_freezed:
                raise serializers.ValidationError(u'Must be unfreezed first')

        return attrs


class UserSerializer(AbstractSerializer):
    remain_days_for_promotion = serializers.CharField(
        source='get_remain_days_for_promotion', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'phone', 'password', 'name', 'point', 'date_joined',
                  'remain_days_for_promotion', 'recommend_code')
        read_only_fields = ('point', 'date_joined', 'recommend_code')
        write_only_fields = ('password',)


class PassengerSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        model = Passenger
        fields = UserSerializer.Meta.fields + ('email', 'ride_count', 'parse_installation_object_id')
        read_only_fields = UserSerializer.Meta.read_only_fields \
                           + ('ride_count',)
        write_only_fields = UserSerializer.Meta.write_only_fields \
                            + ('parse_installation_object_id',)


class DriverSerializer(UserSerializer):
    image_url = serializers.CharField(source='url', read_only=True)
    taxi_service = SeparatedField(source='taxi_service')

    class Meta(UserSerializer.Meta):
        model = Driver
        fields = UserSerializer.Meta.fields + (
            'license_number', 'car_number', 'car_model', 'company',
            'max_capacity', 'taxi_type', 'taxi_service', 'about',
            'rated_count', 'ride_count', 'image_url')
        read_only_fields = UserSerializer.Meta.read_only_fields \
                           + ('rated_count', 'ride_count')
