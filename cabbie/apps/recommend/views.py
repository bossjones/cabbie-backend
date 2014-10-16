# encoding: utf8

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from rest_framework import viewsets

from cabbie.apps.account.models import User, Passenger, Driver
from cabbie.apps.account.serializers import (
    PassengerSerializer, DriverSerializer)
from cabbie.apps.recommend.models import Recommend
from cabbie.apps.recommend.serializers import RecommendSerializer
from cabbie.common.views import APIView


# REST
# ----

class RecommendViewSet(viewsets.ModelViewSet):
    queryset = (Recommend.objects
                .prefetch_related('recommender')
                .prefetch_related('recommendee')
                .all())
    serializer_class = RecommendSerializer
    filter_fields = ('recommend_type', 'created_at')
    ordering = ('-created_at',)

    def get_queryset(self):
        user = self.request.user
        if user.has_role('passenger'):
            user = user.get_role('passenger')
        elif user.has_role('driver'):
            user = user.get_role('driver')

        qs = self.queryset.filter(
            recommender_content_type=ContentType.objects.get_for_model(
                user.__class__),
            recommender_object_id=user.id,
        )
        return qs


class RecommendQueryView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            user = User.objects.get(code=request.GET['code'])
        except User.DoesNotExist:
            return self.render_error(u'유효하지 않은 코드입니다')

        user = user.concrete
        serializer_class = (
            PassengerSerializer if isinstance(user, Passenger) else
            DriverSerializer)
        data = serializer_class(user).data

        point = settings.POINTS_BY_TYPE['recommend_p2p']

        return self.render({
            'user': data,
            'point': point,
        })
