# encoding: utf8

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from cabbie.apps.account.models import User, Passenger, Driver, PassengerDropout
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


class RecommendQueryAmountView(APIView):
    permission_classes = (AllowAny,)

    allowed_types = [
        'recommend_p2p',
        'recommend_p2d',
        'recommend_d2p',
        'recommend_d2d',
        'recommended_p2p',
        'recommended_p2d',
        'recommended_d2p',
        'recommended_d2d',
    ]

    def get(self, request, *args, **kwargs):

        recommend_type = request.GET.get('recommend_type')

        if recommend_type is None or not isinstance(recommend_type, basestring):
            return self.render_error(u'"recommend_type" is needed')

        if recommend_type not in self.allowed_types:
            return self.render_error(u'"recommend_type" you input is not allowed')

        amount = settings.POINTS_BY_TYPE.get(recommend_type)
        amount = amount or 0

        return self.render({ 'amount': amount })


class RecommendQueryView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        phone = request.GET.get('phone')
        recommend_code = request.GET.get('code')

        # param check
        if phone is None or recommend_code is None:
            return self.render_error(u'"phone", "code"를 파라미터로 입력해야 합니다.')
        
        # code existence
        try:
            user = User.objects.get(recommend_code=request.GET['code'])
        except User.DoesNotExist:
            return self.render_error(u'유효하지 않은 코드입니다')
        
        # role check
        if 'recommendee_role' not in request.GET:
            return self.render_error(u'recommendee_role을 입력해주세요')

        recommendee_role = request.GET['recommendee_role']

        if recommendee_role not in ['passenger', 'driver']:
            return self.render_error(u'올바르지 않은 피추천인 타입입니다')

        user = user.concrete

        # dropout history check  (only check in passenger case at this moment @20151104)
        if isinstance(user, Passenger):        
            dropouts = PassengerDropout.objects.all()

            for dropout in dropouts:
                note = dropout.note
        
                if note:
                    dropout_name, dropout_phone = note.split() 

                    if phone == dropout_phone:
                        return self.render_error(u'부정사용 방지를 위하여, 탈퇴한 이력이 있는 경우 추천코드를 입력하실 수 없습니다.')



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
