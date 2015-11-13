# encoding: utf8

from django.contrib import admin
from django.utils import timezone

from cabbie.apps.event.models import RidePointEvent, CuEventPassengers
from cabbie.common.admin import AbstractAdmin

class RidePointEventAdmin(AbstractAdmin):
    list_display = ('priority', 'name', 'starts_at', 'ends_at', 'is_first_come_first_served_basis',
                    'event_point', 'capacity', 'applied_count', 'is_accomplished', 'status')

    fieldsets = (
        (None, {'fields': (
            'name', 'starts_at', 'ends_at', 'is_first_come_first_served_basis', 'capacity', 'event_point', 'priority' 
        )}),
        ('제한조건', {'fields':(
            'specification_type', 'specification_limit_count',
        )}),
        ('읽기전용', {'fields': (
            'applied_count', 'is_accomplished', 
        )}),
    )  

    readonly_fields = ('applied_count', 'is_accomplished',)

    def status(self, obj):
        now = timezone.now()
        if now < obj.starts_at:
            return u'시작전'
        if now >= obj.starts_at and now < obj.ends_at:
            return u'진행중' 
        else:
            return u'종료'
    status.short_description = u'상태'
 

class CuEventPassengersAdmin(AbstractAdmin):
    list_display = ('id', 'passenger', 'passenger_email', 'code', 'created_at', 'is_gift_sent', 'gift_sent_at', 'pin_no', 'api_response_code', 'auth_id', 'auth_date', 'is_issue_canceled') 

    actions = (
        'action_gift_sent',
        'action_gift_sent_cancel',
    )

    def passenger_email(self, obj):
        return obj.passenger.email if obj.passenger else None
    passenger_email.short_description = u'이메일'

    def action_gift_sent(self, request, queryset):
        passengers = list(queryset.all())
        for passenger in passengers:
            passenger.make_gift_sent()
        msg = u'{0}명의 CU 이벤트 승객을 기프티콘 전송완료 처리하였습니다.'.format(len(passengers))
        self.message_user(request, msg)
    action_gift_sent.short_description= u'기프티콘 전송완료 처리'


    def action_gift_sent_cancel(self, request, queryset):
        passengers = list(queryset.all())
        for passenger in passengers:
            passenger.make_gift_sent(sent=False)
        msg = u'{0}명의 CU 이벤트 승객을 기프티콘 전송완료 취소하였습니다.'.format(len(passengers))
        self.message_user(request, msg)
    action_gift_sent_cancel.short_description= u'기프티콘 전송완료 취소'


admin.site.register(RidePointEvent, RidePointEventAdmin)
admin.site.register(CuEventPassengers, CuEventPassengersAdmin)
