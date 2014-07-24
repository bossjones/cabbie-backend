from rest_framework import viewsets, status
from rest_framework.response import Response

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
