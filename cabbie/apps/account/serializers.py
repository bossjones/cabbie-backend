from rest_framework import serializers
from rest_framework.authtoken.serializers import (
    AuthTokenSerializer as BaseAuthTokenSerializer)

from cabbie.apps.account.models import User, Passenger, Driver
from cabbie.common.serializers import AbstractSerializer


class AuthTokenSerializer(BaseAuthTokenSerializer):
    def validate(self, attrs):
        attrs = super(AuthTokenSerializer, self).validate(attrs)

        driver = attrs['user'].get_role('driver')
        if driver:
            if not driver.is_verified:
                raise serializers.ValidationError(u'Must be verified first')
            if not driver.is_accepted:
                raise serializers.ValidationError(u'Must be accepted first')

        return attrs


class UserSerializer(AbstractSerializer):
    class Meta:
        model = User
        fields = ('id', 'phone', 'password', 'name', 'date_joined')
        read_only_fields = ('date_joined',)
        write_only_fields = ('password',)


class PassengerSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        model = Passenger
        fields = UserSerializer.Meta.fields + ('email', 'ride_count')
        read_only_fields = UserSerializer.Meta.read_only_fields \
                           + ('ride_count',)
        write_only_fields = UserSerializer.Meta.write_only_fields \
                            + ('email',)


class DriverSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        model = Driver
        fields = UserSerializer.Meta.fields + ('license_number', 'car_number', 'company', 'bank_account', 'ride_count')
        read_only_fields = UserSerializer.Meta.read_only_fields \
                           + ('ride_count',)
