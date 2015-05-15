# -*- coding: utf-8 -*-
from django.conf import settings
from rest_framework import viewsets

from cabbie.apps.payment.models import PassengerReturn, Transaction, DriverBill, DriverCoupon
from cabbie.apps.payment.serializers import (
    PassengerReturnSerializer, TransactionSerializer, DriverBillSerializer, DriverCouponSerializer)
from cabbie.apps.payment import messages
from cabbie.common.views import CsrfExcempt
from cabbie.utils.email import send_email

# REST
# ----

class PassengerReturnViewSet(CsrfExcempt, viewsets.ModelViewSet):
    queryset = (PassengerReturn.objects
                .prefetch_related('user')
                .all()) 
    serializer_class = PassengerReturnSerializer
    filter_fields = ('is_processed',)
    ordering = ('-created_at',)

    def create(self, request):
        # send apply form email
        user = request.user.concrete
        
        send_email('mail/point/point_application.html', user.email, {
            # common
            'cdn_url': settings.EMAIL_CDN_DOMAIN_NAME,
            'email_font': settings.EMAIL_DEFAULT_FONT,
            'bktaxi_web_url': settings.BKTAXI_WEB_URL,
            'bktaxi_facebook_url': settings.BKTAXI_FACEBOOK_URL,
            'bktaxi_instagram_url': settings.BKTAXI_INSTAGRAM_URL,
            'bktaxi_naver_blog_url': settings.BKTAXI_NAVER_BLOG_URL,

            'subject': messages.PAYMENT_EMAIL_SUBJECT_POINT_APPLICATION,
            'point_application_url': settings.POINT_APPLICATION_URL,
        })        
       
        return super(PassengerReturnViewSet, self).create(request)

        

    def pre_save(self, obj):
        obj.user = self.request.user.get_role('passenger')

    def get_queryset(self):
        user = self.request.user
        qs = self.queryset.filter(user=user)
        return qs

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = (Transaction.objects
                .prefetch_related('user')
                .prefetch_related('ride__passenger')
                .prefetch_related('ride__driver')
                .prefetch_related('recommend__recommender')
                .prefetch_related('recommend__recommendee')
                .all())
    serializer_class = TransactionSerializer
    filter_fields = ('transaction_type', 'created_at')
    ordering = ('-created_at',)

    paginate_by = 1000

    def get_queryset(self):
        user = self.request.user
        if user.has_role('passenger'):
            user = user.get_role('passenger')
        elif user.has_role('driver'):
            user = user.get_role('driver')

        qs = self.queryset.filter(user=user)
        return qs


class DriverBillViewSet(viewsets.ModelViewSet):
    queryset = (DriverBill.objects
                .prefetch_related('driver').all())
    serializer_class = DriverBillSerializer
    ordering = ('-created_at',)

    def get_queryset(self):
        return self.queryset.filter(driver=self.request.user)


class DriverCouponViewSet(viewsets.ModelViewSet):
    queryset = (DriverCoupon.objects
                .prefetch_related('driver').all())
    serializer_class = DriverCouponSerializer
    ordering = ('-created_at',)

    def get_queryset(self):
        return self.queryset.filter(driver=self.request.user)
