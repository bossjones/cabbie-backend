# -*- coding: utf-8 -*-
import datetime
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from cabbie.apps.notice.serializers import NoticeSerializer, AppPopupSerializer
from cabbie.apps.notice.models import Notice, AppPopup

class NoticeViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = Notice.objects.all() 
    serializer_class = NoticeSerializer
    ordering = ('-visible_from',)

    def get_queryset(self):
        # visible_from
        qs = self.queryset
        now = datetime.datetime.now()
        qs = qs.filter(visible_from__lte=now, is_active=True)

        # visibility
        user = self.request.user
    
        if user.has_role('passenger'):
            qs = qs.filter( Q(visibility=Notice.VISIBILITY_PASSENGER) | Q(visibility=Notice.VISIBILITY_ALL))

        elif user.has_role('driver'):
            qs = qs.filter( Q(visibility=Notice.VISIBILITY_DRIVER) | Q(visibility=Notice.VISIBILITY_ALL))

        else:
            qs = qs.filter(visibility=Notice.VISIBILITY_ALL)       
 
        return qs

class AppPopupViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = AppPopup.objects.all() 
    serializer_class = AppPopupSerializer
    ordering = ('starts_at',)

    def get_queryset(self):
        qs = self.queryset

        # filter by now
        now = datetime.datetime.now()
        qs = qs.filter(starts_at__lte=now, ends_at__gte=now, is_active=True)
        return qs
