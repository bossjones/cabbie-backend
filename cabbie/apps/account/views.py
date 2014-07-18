from rest_framework import viewsets, status
from rest_framework.response import Response

from cabbie.apps.account.models import User
from cabbie.apps.account.serializers import UserSerializer


# REST
# ----

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA,
                                         files=request.FILES)
        if serializer.is_valid():
            User.objects.create_user(**serializer.init_data)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED,
                            headers=headers)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
