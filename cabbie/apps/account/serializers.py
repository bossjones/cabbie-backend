from cabbie.apps.account.models import User
from cabbie.common.serializers import AbstractSerializer


class UserSerializer(AbstractSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'name', 'date_joined')
        read_only_fields = ('date_joined',)
        write_only_fields = ('email',)
