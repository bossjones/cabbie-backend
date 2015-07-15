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
                # app_version
                user.app_version = app_version
                update_fields = ['app_version']

                # device_type
                device_type = kwargs.get('device_type')
                if device_type:
                    user.device_type = device_type
                    update_fields.append('device_type')

                user.save(update_fields=update_fields)



class AndroidDriverView(AbstractApplicationVersionView):

    def get(self, request, *args, **kwargs):
        super(AndroidDriverView, self).get(request, *args, **kwargs)

        # get latest version and whether update is required
        ordered = AndroidDriver.objects.order_by('-version_code')
        
        if not ordered:
            return self.render_error(u'No android driver app version found')

        is_update_required = False
        app_version = request.GET.get('app_version', None)

        if app_version:
            for version in ordered:
                if version.version_name == app_version:
                    break
                is_update_required = is_update_required or version.is_update_required
        
        latest = AndroidDriverSerializer(ordered[0]).data
        latest['is_update_required'] = latest['is_update_required'] or is_update_required

        return self.render({
            'latest': latest 
        })

class AndroidPassengerView(AbstractApplicationVersionView):

    def get(self, request, *args, **kwargs):
        # device_type
        kwargs.update({'device_type': 'a'})

        super(AndroidPassengerView, self).get(request, *args, **kwargs)

        # get latest version and whether update is required
        ordered = AndroidPassenger.objects.order_by('-version_code') 

        if not ordered:
            return self.render_error(u'No android passenger app version found')

        is_update_required = False
        app_version = request.GET.get('app_version', None)

        if app_version:
            for version in ordered:
                if version.version_name == app_version:
                    break
                is_update_required = is_update_required or version.is_update_required
        
        latest = AndroidPassengerSerializer(ordered[0]).data
        latest['is_update_required'] = latest['is_update_required'] or is_update_required

        return self.render({
            'latest': latest 
        })

class IosPassengerView(AbstractApplicationVersionView):

    def get(self, request, *args, **kwargs):
        # device_type
        kwargs.update({'device_type': 'i'})

        super(IosPassengerView, self).get(request, *args, **kwargs)

        ordered = IosPassenger.objects.order_by('-version_code') 
        
        if ordered:
            return self.render({
                'latest': IosPassengerSerializer(ordered[0]).data
            })
        else:
            return self.render_error(u'No ios passenger app version found')

