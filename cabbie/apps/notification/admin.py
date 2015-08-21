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


class NotificationPassengerAdmin(AbstractAdmin):
    inlines = [
        NotificationPassengerInline,
    ]
    list_display = ('id', 'notification_type', 'body', 'is_all_passengers',
                    'notified_passenger_count',
                    'created_at')
    list_filter = ('notification_type', 'is_all_passengers', 
                   'created_at',)
    search_fields = ('=id', 'body')
    fieldsets = (
        (None, {'fields': (
            'notification_type', 'body', 'is_all_passengers', 
        )}),
        ('읽기전용', {'fields': (
            'notified_passenger_count', 'created_at'
        )}),
    )
    readonly_fields = ('notified_passenger_count', 
                       'created_at',)

    def response_add(self, request, obj, post_url_continue=None):
        ret = super(NotificationPassengerAdmin, self).response_add(
            request, obj, post_url_continue)
        notification_created.send(sender=self.__class__, notification=obj)
        return ret

    def get_queryset(self, request):
        qs = self.model._default_manager.get_queryset()
        return qs.filter(notified_passenger_count__gt=0)        


class NotificationDriverAdmin(AbstractAdmin):
    inlines = [
        NotificationDriverInline,
    ]
    list_display = ('id', 'notification_type', 'body', 
                    'is_all_drivers', 
                    'is_freezed', 'education', 'province', 'region',
                    'is_test',
                    'notified_driver_count', 'created_at')
    list_filter = ('notification_type', 'is_all_drivers',
                   'created_at',)
    search_fields = ('=id', 'body')
    fieldsets = (
        (None, {'fields': (
            'body', 'is_all_drivers',
            'is_freezed', 'education', 'province', 'region',
            'is_test',
        )}),
        ('읽기전용', {'fields': (
            'notified_driver_count', 'created_at'
        )}),
    )
    readonly_fields = ('notified_driver_count',
                       'created_at',)

    def response_add(self, request, obj, post_url_continue=None):
        ret = super(NotificationDriverAdmin, self).response_add(
            request, obj, post_url_continue)
        notification_created.send(sender=self.__class__, notification=obj)
        return ret

    def get_queryset(self, request):
        qs = self.model._default_manager.get_queryset()
        return qs.filter(notified_driver_count__gt=0)        


# proxy model of Notification to allow double register
class ProxyNotification(Notification):
    class Meta:
        proxy = True
        verbose_name = u'기사SMS알림'
        verbose_name_plural = u'기사SMS알림'

admin.site.register(Notification, NotificationPassengerAdmin)
admin.site.register(ProxyNotification, NotificationDriverAdmin)
