from rest_framework import serializers

from cabbie.apps.account.serializers import (
    DriverSerializer, PassengerSerializer)
from cabbie.apps.recommend.models import Recommend
from cabbie.common.serializers import AbstractSerializer


class RecommendSerializer(AbstractSerializer):
    recommender = serializers.SerializerMethodField('get_recommender')
    recommendee = serializers.SerializerMethodField('get_recommendee')

    class Meta:
        model = Recommend
        fields = ('id', 'recommender', 'recommendee', 'recommend_type',
                  'created_at')

    def get_recommender(self, obj):
        return self._get_user(obj.recommender)

    def get_recommendee(self, obj):
        return self._get_user(obj.recommendee)

    def _get_user(self, user):
        if user.has_role('passenger'):
            return PassengerSerializer(user).data
        elif user.has_role('driver'):
            return DriverSerializer(user).data
        else:
            raise Exception('Unknown user role')
