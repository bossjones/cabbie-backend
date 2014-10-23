from django.shortcuts import render
from rest_framework.permissions import AllowAny

from cabbie.common.views import InternalView, APIView, APIMixin
from cabbie.apps.appversion.models import AndroidDriver
from cabbie.apps.appversion.serializers import AndroidDriverSerializer

# REST
# ----

class AndroidDriverView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        latest = AndroidDriver.objects.order_by('-version_code')[0] 
        
        if latest:
            return self.render({
                'latest': AndroidDriverSerializer(latest).data
            })
        
        
