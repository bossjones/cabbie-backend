from rest_framework import serializers


class JSONField(serializers.WritableField):
    pass


class AbstractSerializer(serializers.ModelSerializer):
    @property
    def auth_user(self):
        return self.context['request'].user
