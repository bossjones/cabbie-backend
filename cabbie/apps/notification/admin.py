# encoding: utf8

from django.contrib import admin

from cabbie.apps.account.models import Passenger
from cabbie.apps.notification.models import Notification
from cabbie.apps.notification.signals import notification_created
from cabbie.common.admin import AbstractAdmin


class NotificationPassengerInline(admin.TabularInline):
    model = Notification.passengers.through
    extra = 1
    raw_id_fields = ('passenger',)


class NotificationDriverInline(admin.TabularInline):
    model = Notification.drivers.through
    extra = 1
    raw_id_fields = ('driver',)


class NotificationAdmin(AbstractAdmin):
    inlines = [
        NotificationPassengerInline,
        NotificationDriverInline,
    ]
    list_display = ('id', 'notification_type', 'body', 'is_all_passengers',
                    'is_all_drivers', 'notified_passenger_count',
                    'notified_driver_count', 'created_at')
    list_filter = ('notification_type', 'is_all_passengers', 'is_all_drivers',
                   'created_at',)
    search_fields = ('=id', 'body')
    fieldsets = (
        (None, {'fields': (
            'notification_type', 'body', 'is_all_passengers', 'is_all_drivers',
        )}),
        ('읽기전용', {'fields': (
            'notified_passenger_count', 'notified_driver_count', 'created_at'
        )}),
    )
    readonly_fields = ('notified_passenger_count', 'notified_driver_count',
                       'created_at',)

    def response_add(self, request, obj, post_url_continue=None):
        ret = super(NotificationAdmin, self).response_add(
            request, obj, post_url_continue)
        notification_created.send(sender=self.__class__, notification=obj)
        return ret


admin.site.register(Notification, NotificationAdmin)
