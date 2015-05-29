from cabbie.apps.appversion.models import AndroidDriver, AndroidPassenger, IosPassenger
from cabbie.common.serializers import AbstractSerializer


class AbstractApplicationVersionSerializer(AbstractSerializer):
    class Meta:
        fields = ('version_code', 'version_name', 'is_update_required')

class AndroidDriverSerializer(AbstractApplicationVersionSerializer):
    class Meta(AbstractApplicationVersionSerializer.Meta):
        model = AndroidDriver

class AndroidPassengerSerializer(AbstractApplicationVersionSerializer):
    class Meta(AbstractApplicationVersionSerializer.Meta):
        model = AndroidPassenger

class IosPassengerSerializer(AbstractApplicationVersionSerializer):
    class Meta(AbstractApplicationVersionSerializer.Meta):
        model = IosPassenger
