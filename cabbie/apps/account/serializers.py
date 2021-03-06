from rest_framework import serializers
from rest_framework.authtoken.serializers import (
    AuthTokenSerializer as BaseAuthTokenSerializer)

from cabbie.apps.affiliation.serializers import AffiliationSerializer

from cabbie.apps.account.models import User, Passenger, Driver
from cabbie.common.serializers import AbstractSerializer, SeparatedField, JSONField


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
    has_unread_notices = serializers.Field(source='has_unread_notices')
    class Meta:
        model = User
        fields = ('id', 'phone', 'password', 'name', 'is_sms_agreed', 'is_email_agreed', 'point', 
                'date_joined', 'recommend_code', 'has_unread_notices')
        read_only_fields = ('point', 'date_joined', 'recommend_code')
        write_only_fields = ('password',)


class PassengerSerializer(UserSerializer):
    latest_ride = JSONField(source='latest_ride', read_only=True) 
    affiliation = AffiliationSerializer(read_only=True)

    class Meta(UserSerializer.Meta):
        model = Passenger
        fields = UserSerializer.Meta.fields + ('email', 'latest_ride', 'affiliation') 


class DriverSerializer(UserSerializer):
    image_urls = serializers.CharField(source='get_image_urls', read_only=True)
    latest_ride = JSONField(source='latest_ride', read_only=True) 
    rating = serializers.Field(source='rating')
    ratings_by_category = JSONField(source='ratings_by_category')
    rated_count = serializers.Field(source='rated_count')
    ride_count = serializers.Field(source='ride_count')

    class Meta(UserSerializer.Meta):
        model = Driver
        fields = UserSerializer.Meta.fields + (
            'license_number', 'car_number', 'car_model', 'company',
            'max_capacity', 'taxi_type', 'about',
            'rating', 'ratings_by_category', 'rated_count', 'ride_count', 'image_urls', 'latest_ride')
