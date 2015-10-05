from rest_framework import serializers

from cabbie.apps.notice.models import Notice, AppPopup
from cabbie.common.serializers import AbstractSerializer

class NoticeSerializer(AbstractSerializer):
    image_url = serializers.CharField(source='url', read_only=True)
    is_new = serializers.Field(source='is_new')
    class Meta:
        model = Notice
        fields = ('id', 'title', 'notice_type', 'content', 'image_url', 'image_width', 'image_height', 'link', 'link_label', 'visible_from', 'is_new')

class AppPopupSerializer(AbstractSerializer):
    image_url = serializers.CharField(source='url', read_only=True)
    class Meta:
        model = AppPopup
        fields = ('id', 'title', 'content', 'image_url', 'image_width', 'image_height', 'link')
