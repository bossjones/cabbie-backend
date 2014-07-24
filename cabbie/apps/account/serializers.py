from cabbie.apps.account.models import User, Passenger, Driver
from cabbie.common.serializers import AbstractSerializer


class UserSerializer(AbstractSerializer):
    class Meta:
        model = User
        fields = ('id', 'phone', 'password', 'name', 'date_joined')
        read_only_fields = ('date_joined',)
        write_only_fields = ('phone', 'password')


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
        fields = UserSerializer.Meta.fields + ('licence_number', 'ride_count')
        read_only_fields = UserSerializer.Meta.read_only_fields \
                           + ('ride_count',)
