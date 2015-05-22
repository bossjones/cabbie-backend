from rest_framework import serializers

from cabbie.apps.notice.models import Notice, AppPopup
from cabbie.common.serializers import AbstractSerializer

class NoticeSerializer(AbstractSerializer):
    class Meta:
        model = Notice
        fields = ('id', 'title', 'content', 'visible_from')

class AppPopupSerializer(AbstractSerializer):
    image_url = serializers.CharField(source='url', read_only=True)
    class Meta:
        model = AppPopup
        fields = ('id', 'title', 'content', 'image_url', 'link')
