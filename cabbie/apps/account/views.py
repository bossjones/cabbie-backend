# encoding: utf-8

import re
import datetime

from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser
from rest_framework.authtoken.views import (
    ObtainAuthToken as BaseObtainAuthToken)
from rest_framework.authtoken.models import Token
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from cabbie.apps.account import messages
from cabbie.apps.account.models import User, Passenger, Driver, PassengerDropout, DriverDropout, DriverReservation
from cabbie.apps.account.serializers import (
    AuthTokenSerializer, PassengerSerializer, DriverSerializer)
from cabbie.apps.account.session import (
    PhoneVerificationSessionManager, PasswordResetSessionManager, InvalidCode, InvalidSession)
from cabbie.apps.recommend.models import Recommend
from cabbie.common.views import APIMixin, APIView, GenericAPIView
from cabbie.utils.ds import pick
from cabbie.utils.sms import send_sms
from cabbie.utils.email import send_email
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

class DriverAuthView(ObtainAuthToken):
    serializer_class = AuthTokenSerializer
    
    def post(self, request):
        # add password for all drivers
        if request.DATA.get('password', None):
            return Response({'error': 'password is not allowed parameter'}, status=status.HTTP_400_BAD_REQUEST)
        
        _credential = dict()
        _credential['password'] = Driver.get_login_key()
        _credential['username'] = request.DATA['username'] 
       
        serializer = self.serializer_class(data=_credential)
        if serializer.is_valid():
            token, created = Token.objects.get_or_create(user=serializer.object['user'])
            return Response({'token':token.key, 'id':token.user.id})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PassengerAuthView(ObtainAuthToken):
    serializer_class = AuthTokenSerializer
    

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
        # master verification code
        if request.DATA['verification_code'] == settings.MASTER_VERIFICATION_CODE:
            pass
        elif driver.verification_code != request.DATA['verification_code']:
            return self.render_error('Invalid verification code')

        driver.is_verified = True
        driver.save()

        return self.render({
            'login_key': Driver.get_login_key(),
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

        # recommendation
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

        driver.is_accepted = True
        driver.is_sms_agreed = request.DATA['is_sms_agreed']
        driver.save()

        # send welcome sms
        if driver.is_sms_agreed:
            send_sms('sms/driver_accept.txt', driver.phone, {})
            send_sms('sms/driver_accept_2.txt', driver.phone, {})

        return self.render()

class UserDropoutView(APIView):
    def post(self, request, *args, **kwargs):
        user = request.user.concrete
        if isinstance(user, Passenger):
            user.dropout(PassengerDropout.REQUEST)
        elif isinstance(user, Driver):
            user.dropout(DriverDropout.REQUEST)

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
                u'정상적인 휴대폰 번호가 아닙니다 (숫자만 입력해 주세요)')

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

class PasswordResetActivateView(GenericAPIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        try:
            # reset password
            phone = request.DATA['phone']
            phone = re.sub(r'[^\d]', '', phone)
            user = User.objects.get(phone=phone)             

            # create session
            PasswordResetSessionManager().create(request.DATA['phone'])

        except Exception as e:
            return self.render_error(u'오류가 발생했습니다: {0}'.format(e))
        else:
            return self.render()

class PasswordResetView(GenericAPIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        try:
            # reset password
            phone = request.DATA['phone']
            phone = re.sub(r'[^\d]', '', phone)
            user = User.objects.get(phone=phone)             
            
            user.set_password(request.DATA['new_password'])
            user.save()

            # clear session
            PasswordResetSessionManager().reset(request.DATA['phone'])

            # send email
            send_email('mail/password_changed.html', user.concrete.email, {
                # common
                'cdn_url': settings.EMAIL_CDN_DOMAIN_NAME,
                'email_font': settings.EMAIL_DEFAULT_FONT,
                'bktaxi_web_url': settings.BKTAXI_WEB_URL,
                'bktaxi_facebook_url': settings.BKTAXI_FACEBOOK_URL,
                'bktaxi_instagram_url': settings.BKTAXI_INSTAGRAM_URL,
                'bktaxi_naver_blog_url': settings.BKTAXI_NAVER_BLOG_URL,

                'subject': messages.ACCOUNT_EMAIL_SUBJECT_PASSWORD_CHANGED,
                'changed_at': datetime.datetime.now(),
            })
            
        except InvalidSession:
            return self.render_error(
                u'비밀번호 재설정 세션이 만료되었습니다. 처음부터 다시 시작해주세요.')
        except Exception as e:
            return self.render_error(u'오류가 발생했습니다: {0}'.format(e))
        else:
            return self.render()

class UserQueryView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        phone = request.GET.get('phone', None)
        
        if phone:
            try: 
                user = User.objects.get(phone=phone)
            except User.DoesNotExist:
                return self.render()
            else:
                return self.render_error(u'이미 등록된 휴대폰 번호입니다. 로그인 후 사용해 주세요.')

        email = request.GET.get('email', None)

        if email:
            try:
                passenger = Passenger.objects.get(email=email)
            except Passenger.DoesNotExist:
                return self.render()
            else:
                return self.render_error(u'이미 등록된 이메일입니다. 다른 이메일을 입력해 주세요.')

        existing_phone = request.GET.get('existing_phone', None)

        if existing_phone:
            try: 
                user = User.objects.get(phone=existing_phone)
            except User.DoesNotExist:
                return self.render_error(u'가입되지 않은 휴대폰 번호입니다.')
            else:
                return self.render()


        return self.render_error('phone 또는 email을 입력해 주세요.') 
  
class UserUpdatePushIdView(APIView):
    def post(self, request, *args, **kwargs):
        
        try:
            user = User.objects.get(pk=request.user.id)
        except User.DoesNotExist:
            return self.render_error('Not authenticated user')
        else:
            push_id = '{0}_user_{1}'.format(request.DATA['prefix'], request.user.id)
            user.push_id = push_id
            user.save(update_fields=['push_id'])

            return self.render()

class DriverReserveView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        driver, created = DriverReservation.objects.get_or_create(phone=request.DATA['phone'], 
                                                                  name=request.DATA['name'], 
                                                                  car_model=request.DATA['car_model'])
        return self.render({
            'reservation_id': driver.id
        })

class DriverReserveUploadCertificateView(APIView):
    permission_classes = (AllowAny,)
    parser_classes = (MultiPartParser,)

    def post(self, request, reservation_id, *args, **kwargs):

        file_obj = request.FILES['upload_file']
        file_name = request.DATA['filename']

        import mimetypes
        content_type, encoding = mimetypes.guess_type(file_name)
        file_obj.content_type = content_type
        file_obj._name = file_name

        print reservation_id

        driver = DriverReservation.objects.get(id=reservation_id)
        driver.image = file_obj
        driver.save()

        return self.render({
            'uploaded_url': driver.url
        })

