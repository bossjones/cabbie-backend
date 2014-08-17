from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView

from cabbie.apps.account.models import User, Passenger, Driver
from cabbie.apps.account.serializers import (
    UserSerializer, PassengerSerializer, DriverSerializer)
from cabbie.utils.ds import pick


# REST
# ----

class AbstractUserViewSet(viewsets.ModelViewSet):
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


class DriverViewSet(AbstractUserViewSet):
    model = Driver
    serializer_class = DriverSerializer


class DriverVerifyView(APIView):
    def _render_error(self, msg):
        return Response({'error':msg}, status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request, *args, **kwargs):
        try:
            driver = Driver.objects.get(phone=request.DATA['phone'])
        except Driver.DoesNotExist as e:
            return self._render_error(unicode(e))
        if driver.is_verified:
            return self._render_error('Already verified')
        if driver.verification_code != request.DATA['verification_code']:
            return self._render_error('Invalid verification code')

        driver.is_verified = True
        driver.save()

        return Response({'login_key': driver.get_login_key()})
