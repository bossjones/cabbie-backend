import datetime

from django.contrib.gis.geos import Point
from django.utils import timezone
from rest_framework import serializers

from cabbie.utils import json


class JSONField(serializers.WritableField):
    pass


class PointField(serializers.WritableField):
    def to_native(self, obj):
        return obj.coords

    def from_native(self, data):
        as_json = json.loads(data)
        return Point(*as_json)


class AbstractSerializer(serializers.ModelSerializer):
    @property
    def auth_user(self):
        return self.context['request'].user

    def to_native(self, obj):
        ret = super(AbstractSerializer, self).to_native(obj)
        for key in ret:
            value = ret[key]
            if isinstance(value, datetime.datetime) and value.tzinfo:
                ret[key] = timezone.get_current_timezone().normalize(value)
        return ret
