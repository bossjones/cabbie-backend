from rest_framework import serializers

from cabbie.apps.affiliation.models import Affiliation
from cabbie.common.serializers import AbstractSerializer


class AffiliationSerializer(AbstractSerializer):
    image_urls = serializers.CharField(source='get_image_urls', read_only=True)

    class Meta:
        model = Affiliation 
        fields = ('name', 'certificate_code', 'ride_mileage', 'is_active')
