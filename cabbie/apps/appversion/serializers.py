from cabbie.apps.appversion.models import AndroidDriver, AndroidPassenger
from cabbie.common.serializers import AbstractSerializer


class AbstractAndroidApplicationVersionSerializer(AbstractSerializer):
    class Meta:
        fields = ('version_code', 'version_name', 'is_update_required')

class AndroidDriverSerializer(AbstractAndroidApplicationVersionSerializer):
    class Meta(AbstractAndroidApplicationVersionSerializer.Meta):
        model = AndroidDriver

class AndroidPassengerSerializer(AbstractAndroidApplicationVersionSerializer):
    class Meta(AbstractAndroidApplicationVersionSerializer.Meta):
        model = AndroidPassenger
