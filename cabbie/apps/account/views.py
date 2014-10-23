# encoding: utf-8

import re

from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser
from rest_framework.authtoken.views import (
    ObtainAuthToken as BaseObtainAuthToken)
from rest_framework.authtoken.models import Token
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from cabbie.apps.account.models import User, Passenger, Driver, DriverReservation
from cabbie.apps.account.serializers import (
    AuthTokenSerializer, PassengerSerializer, DriverSerializer)
from cabbie.apps.account.session import (
    PhoneVerificationSessionManager, InvalidCode, InvalidSession)
from cabbie.apps.recommend.models import Recommend
from cabbie.common.views import APIMixin, APIView, GenericAPIView
from cabbie.utils.ds import pick
from cabbie.utils.validator import is_valid_phone
from cabbie.utils import json

# REST (Mixin/Abstract)
# ---------------------

class AbstractUserViewSet(APIMixin, viewsets.ModelViewSet):
    model = None
    serializer_class = None

    def get_queryset(self):
        return self.model.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA,
                                         files=request.FILES)
        if serializer.is_valid():
            self.model.objects.create_user(**pick(serializer.init_data,
                                                  *serializer.Meta.fields))
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED,
                            headers=headers)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AbstractUserSignupView(CreateModelMixin, RetrieveModelMixin, GenericAPIView):
    permission_classes = (AllowAny,)
    model = None
    serializer_class = None

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA,
                                         files=request.FILES)
        if serializer.is_valid():
            user = self.model.objects.create_user(**pick(
                serializer.init_data, *serializer.Meta.fields))

            recommenders = request.DATA.get('recommenders', [])

            recommenders = json.loads(recommenders) if isinstance(recommenders, basestring) else recommenders 
            recommenders = map(int, recommenders)

            for recommender_id in recommenders:
                recommender = User.objects.get(id=recommender_id).concrete
                if not recommender:
                    continue
                Recommend.objects.create(
                    recommender=recommender,
                    recommendee=user,
                )

            headers = self.get_success_headers(serializer.data)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED,
                            headers=headers)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PassengerMixin(object):
    model = Passenger
    serializer_class = PassengerSerializer


class DriverMixin(object):
    model = Driver
    serializer_class = DriverSerializer


# REST (Concrete)
# ---------------

class ObtainAuthToken(BaseObtainAuthToken):
    serializer_class = AuthTokenSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.DATA)
        if serializer.is_valid():
            token, created = Token.objects.get_or_create(user=serializer.object['user'])
            return Response({'token':token.key, 'id':token.user.id})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PassengerViewSet(PassengerMixin, AbstractUserViewSet):        pass
class DriverViewSet(DriverMixin, AbstractUserViewSet):              pass
class PassengerSignupView(PassengerMixin, AbstractUserSignupView):  pass


class DriverVerifyView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        try:
            driver = Driver.objects.get(phone=request.DATA['phone'])
        except Driver.DoesNotExist as e:
            return self.render_error(unicode(e))
        if driver.verification_code != request.DATA['verification_code']:
            return self.render_error('Invalid verification code')

        driver.is_verified = True
        driver.save()

        return self.render({
            'login_key': driver.get_login_key(),
            'driver': DriverSerializer(driver).data
        })


class DriverAcceptView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        try:
            driver = Driver.objects.get(phone=request.DATA['phone'])
        except Driver.DoesNotExist as e:
            return self.render_error(unicode(e))
        if not driver.is_verified:
            return self.render_error('Must be verified first')
        if driver.get_login_key() != request.DATA['login_key']:
            return self.render_error('Invalid login key')

        driver.is_accepted = True
        driver.save()

        return self.render()


class DriverPhotoUploadView(APIView):
    parser_classes = (MultiPartParser,)

    def post(self, request, *args, **kwargs):

        file_obj = request.FILES['upload_file']
        file_name = request.DATA['filename']

        import mimetypes
        content_type, encoding = mimetypes.guess_type(file_name)
        file_obj.content_type = content_type
        file_obj._name = file_name

        driver = Driver.objects.get(id=request.user.id)
        driver.image = file_obj
        driver.save()

        return self.render({
            'uploaded_url': driver.url
        })


class PhoneVerifyIssueView(GenericAPIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        phone = request.DATA['phone']
        phone = re.sub(r'[^\d]', '', phone)
        if not is_valid_phone(phone):
            return self.render_error(
                u'정상적인 휴대폰 번호가 아닙니다 (숫자만 입력해주세요)')

        try:
            code = PhoneVerificationSessionManager().create(
                request.DATA['phone'])
        except Exception as e:
            return self.render_error(u'오류가 발생했습니다: {0}'.format(e))
        else:
            return self.render({'code': code})


class PhoneVerifyCheckView(GenericAPIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        try:
            PhoneVerificationSessionManager().verify(
                request.DATA['phone'], request.DATA['code'])
        except InvalidSession:
            return self.render_error(
                u'세션이 만료되었습니다. 처음부터 다시 시작해주세요.')
        except InvalidCode:
            return self.render_error(
                u'인증번호가 일치하지 않습니다. 다시 확인해주세요.')
        except Exception as e:
            return self.render_error(u'오류가 발생했습니다: {0}'.format(e))
        else:
            return self.render()

class DriverReserveView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        driver, created = DriverReservation.objects.get_or_create(phone=request.DATA['phone'], name=request.DATA['name'])
        return self.render()


