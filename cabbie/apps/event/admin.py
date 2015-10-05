# encoding: utf8

from django.contrib import admin
from django.utils import timezone

from cabbie.apps.event.models import RidePointEvent
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
 

admin.site.register(RidePointEvent, RidePointEventAdmin)
