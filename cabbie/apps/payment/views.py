from rest_framework import viewsets

from cabbie.apps.payment.models import Transaction, DriverBill, DriverCoupon
from cabbie.apps.payment.serializers import (
    TransactionSerializer, DriverBillSerializer, DriverCouponSerializer)


# REST
# ----

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
