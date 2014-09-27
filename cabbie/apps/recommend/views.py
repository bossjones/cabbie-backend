from django.contrib.contenttypes.models import ContentType
from rest_framework import viewsets

from cabbie.apps.recommend.models import Recommend
from cabbie.apps.recommend.serializers import RecommendSerializer


# REST
# ----

class RecommendViewSet(viewsets.ModelViewSet):
    queryset = (Recommend.objects
                .prefetch_related('recommender')
                .prefetch_related('recommendee')
                .all())
    serializer_class = RecommendSerializer
    filter_fields = ('recommend_type', 'created_at')
    ordering = ('-created_at',)

    def get_queryset(self):
        user = self.request.user
        if user.has_role('passenger'):
            user = user.get_role('passenger')
        elif user.has_role('driver'):
            user = user.get_role('driver')

        qs = self.queryset.filter(
            recommender_content_type=ContentType.objects.get_for_model(
                user.__class__),
            recommender_object_id=user.id,
        )
        return qs
