# -*- coding: utf-8 -*-
import datetime
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
        now = datetime.datetime.now()
        return self.queryset.filter(visible_from__lte=now, is_active=True)
        

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
