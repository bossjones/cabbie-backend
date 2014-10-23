from cabbie.apps.appversion.models import AndroidDriver
from cabbie.common.serializers import AbstractSerializer


class AndroidDriverSerializer(AbstractSerializer):
    class Meta:
        model = AndroidDriver 
        fields = ('version_code', 'version_name', 'is_update_required')
