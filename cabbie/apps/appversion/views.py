from django.shortcuts import render
from rest_framework.permissions import AllowAny

from cabbie.common.views import InternalView, APIView, APIMixin
from cabbie.apps.appversion.models import AndroidDriver, AndroidPassenger, IosPassenger
from cabbie.apps.appversion.serializers import (AndroidDriverSerializer, AndroidPassengerSerializer, IosPassengerSerializer)
from cabbie.apps.account.models import User

# REST
# ----

class AbstractApplicationVersionView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        
        app_version = request.GET.get('app_version', None)
        user_id = request.GET.get('id', None)

        if app_version is not None and user_id is not None:
            try:
                user = User.objects.get(pk=user_id)
            except User.DoesNotExist, e:
                pass
            else:
                user.app_version = app_version
                user.save(update_fields=['app_version'])



class AndroidDriverView(AbstractApplicationVersionView):

    def get(self, request, *args, **kwargs):
        super(AndroidDriverView, self).get(request, *args, **kwargs)

        ordered = AndroidDriver.objects.order_by('-version_code')
        
        if ordered:
            return self.render({
                'latest': AndroidDriverSerializer(ordered[0]).data
            })
        else:
            return self.render_error(u'No android driver app version found')

class AndroidPassengerView(AbstractApplicationVersionView):

    def get(self, request, *args, **kwargs):
        super(AndroidPassengerView, self).get(request, *args, **kwargs)

        ordered = AndroidPassenger.objects.order_by('-version_code') 
        
        if ordered:
            return self.render({
                'latest': AndroidPassengerSerializer(ordered[0]).data
            })
        else:
            return self.render_error(u'No android passenger app version found')

class IosPassengerView(AbstractApplicationVersionView):

    def get(self, request, *args, **kwargs):
        super(IosPassengerView, self).get(request, *args, **kwargs)

        ordered = IosPassenger.objects.order_by('-version_code') 
        
        if ordered:
            return self.render({
                'latest': IosPassengerSerializer(ordered[0]).data
            })
        else:
            return self.render_error(u'No ios passenger app version found')

