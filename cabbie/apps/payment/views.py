from django.contrib.contenttypes.models import ContentType
from rest_framework import viewsets

from cabbie.apps.payment.models import Transaction
from cabbie.apps.payment.serializers import TransactionSerializer


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

    def get_queryset(self):
        user = self.request.user
        if user.has_role('passenger'):
            user = user.get_role('passenger')
        elif user.has_role('driver'):
            user = user.get_role('driver')

        qs = self.queryset.filter(
            user_content_type=ContentType.objects.get_for_model(
                user.__class__),
            user_object_id=user.id,
        )
        return qs
