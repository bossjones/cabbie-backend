# encoding: utf8

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

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
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        try:
            user = User.objects.get(phone=request.GET['code'])
        except User.DoesNotExist:
            return self.render_error(u'유효하지 않은 코드입니다')
        
        if 'recommendee_role' not in request.GET:
            return self.render_error(u'recommendee_role을 입력해주세요')

        recommendee_role = request.GET['recommendee_role']

        if recommendee_role not in ['passenger', 'driver']:
            return self.render_error(u'올바르지 않은 피추천인 타입입니다')

        user = user.concrete

        recommender_role = 'passenger' if isinstance(user, Passenger) else 'driver'

        serializer_class = (
            PassengerSerializer if isinstance(user, Passenger) else
            DriverSerializer)
        data = serializer_class(user).data

        point_key = 'recommended_{0}2{1}'.format(recommender_role[0], recommendee_role[0])
        point = settings.POINTS_BY_TYPE[point_key]

        return self.render({
            'user': data,
            'recommender_role': 'passenger' if isinstance(user, Passenger) else 'driver',
            'point': point,
        })
