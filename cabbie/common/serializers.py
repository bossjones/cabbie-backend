from django.contrib.gis.geos import Point
from rest_framework import serializers


class JSONField(serializers.WritableField):
    pass


class PointField(serializers.WritableField):
    def to_native(self, obj):
        return obj.coords

    def from_native(self, data):
        return Point(*data)


class AbstractSerializer(serializers.ModelSerializer):
    @property
    def auth_user(self):
        return self.context['request'].user
