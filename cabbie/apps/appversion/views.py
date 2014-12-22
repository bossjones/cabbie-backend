from django.shortcuts import render
from rest_framework.permissions import AllowAny

from cabbie.common.views import InternalView, APIView, APIMixin
from cabbie.apps.appversion.models import AndroidDriver, AndroidPassenger
from cabbie.apps.appversion.serializers import AndroidDriverSerializer, AndroidPassengerSerializer

# REST
# ----

class AbstractAndroidApplicationVersionView(APIView):
    permission_classes = (AllowAny,)


class AndroidDriverView(AbstractAndroidApplicationVersionView):

    def get(self, request, *args, **kwargs):
        ordered = AndroidDriver.objects.order_by('-version_code')
        
        if ordered:
            return self.render({
                'latest': AndroidDriverSerializer(ordered[0]).data
            })
        else:
            return self.render()

class AndroidPassengerView(AbstractAndroidApplicationVersionView):

    def get(self, request, *args, **kwargs):
        ordered = AndroidPassenger.objects.order_by('-version_code') 
        
        if ordered:
            return self.render({
                'latest': AndroidPassengerSerializer(ordered[0]).data
            })
        else:
            return self.render()

