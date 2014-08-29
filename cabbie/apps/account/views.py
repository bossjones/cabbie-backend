from rest_framework import viewsets, status
from rest_framework.authtoken.views import (
    ObtainAuthToken as BaseObtainAuthToken)
from rest_framework.response import Response
from rest_framework.permissions import AllowAny 

from cabbie.apps.account.models import Passenger, Driver
from cabbie.apps.account.serializers import (
    AuthTokenSerializer, UserSerializer, PassengerSerializer, DriverSerializer)
from cabbie.common.views import APIMixin, APIView
from cabbie.apps.account.permissions import AllowPostToAny
from cabbie.utils.ds import pick


# REST
# ----

class ObtainAuthToken(BaseObtainAuthToken):
    serializer_class = AuthTokenSerializer


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


class PassengerViewSet(AbstractUserViewSet):
    model = Passenger
    serializer_class = PassengerSerializer
    permission_classes = (AllowPostToAny,)


class DriverViewSet(AbstractUserViewSet):
    model = Driver
    serializer_class = DriverSerializer
    permission_classes = (AllowPostToAny,)


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
