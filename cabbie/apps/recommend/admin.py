from django.contrib import admin

from cabbie.apps.recommend.models import Recommend


class RecommendAdmin(admin.ModelAdmin):
    list_display = ('recommender_', 'recommendee_', 'recommend_type',
                    'created_at')

    def recommender_(self, obj):
        return obj.recommender

    def recommendee_(self, obj):
        return obj.recommendee


admin.site.register(Recommend, RecommendAdmin)
