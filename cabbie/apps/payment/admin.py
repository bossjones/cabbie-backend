# encoding: utf8

from django.contrib import admin

from cabbie.apps.payment.models import (
    DriverBill, DriverCoupon, Transaction, PassengerReturn, DriverReturn)
from cabbie.apps.payment.resources import (
    PassengerReturnResource, DriverReturnResource)
from cabbie.common.admin import AbstractAdmin


class DriverBillAdmin(AbstractAdmin):
    raw_id_fields = ('driver',)
    list_display = ('id', 'driver', 'target_month', 'amount', 'created_at')
    list_filter = ('created_at',)
    search_fields = (
        '=id',
        'driver__name',
        '^driver__phone',
    )
    fieldsets = (
        (None, {'fields': ('driver', 'target_month', 'amount')}),
        ('읽기전용', {'fields': ('created_at',)}),
    )
    readonly_fields = ('created_at',)


class DriverCouponAdmin(AbstractAdmin):
    raw_id_fields = ('driver',)
    list_display = ('id', 'driver', 'previous_month_board_count',
                    'coupon_type', 'coupon_name', 'amount', 'serial_number', 'is_processed',
                    'processed_at', 'created_at')
    list_filter = ('coupon_type', 'is_processed', 'processed_at', 'created_at')
    search_fields = (
        '=id',
        'driver__name',
        '^driver__phone',
        'coupon_name',
    )
    fieldsets = (
        (None, {'fields': ('driver', 'coupon_type', 'coupon_name', 'amount',
                           'serial_number')}),
        ('읽기전용', {'fields': (
            'is_processed', 'processed_at', 'created_at',
        )}),
    )
    readonly_fields = ('is_processed', 'processed_at', 'created_at')
    actions = (
        'process',
    )

    def process(self, request, queryset):
        coupons = list(queryset.all())
        for coupon in coupons:
            coupon.process()
        msg = u'{0}개의 지급 처리를 완료하였습니다.'.format(len(coupons))
        self.message_user(request, msg)
    process.short_description = u'지급완료 처리'

class TransactionAdmin(AbstractAdmin):
    list_filter = ('transaction_type', 'created_at')
    list_display = ('id', 'user', 'transaction_type', 'amount', 'note',
                    'created_at')
    fields = ('user', 'transaction_type',
              'amount', 'note',)
    raw_id_fields = ('user',)


class AbstractReturnAdmin(AbstractAdmin):
    list_filter = ('is_requested', 'is_processed', 'processed_at',
                   'created_at')
    list_display = ('user', 'phone', 'bank_account', 'amount',
                    'is_requested', 'is_processed', 'processed_at',
                    'created_at')
    readonly_fields = ('user', 'amount', 'is_requested', 'is_processed',
                       'processed_at', 'created_at')
    search_fields = (
        '=id',
        '^user__phone',
        'user__name',
    )
    actions = (
        'process',
    )

    def process(self, request, queryset):
        returns = list(queryset.all())
        for return_ in returns:
            return_.process()
        msg = u'{0}개의 환급완료 처리를 완료하였습니다.'.format(len(returns))
        self.message_user(request, msg)
    process.short_description = u'환급완료 처리'


class PassengerReturnAdmin(AbstractReturnAdmin):
    resource_class = PassengerReturnResource


class DriverReturnAdmin(AbstractReturnAdmin):
    resource_class = DriverReturnResource


admin.site.register(DriverBill, DriverBillAdmin)
admin.site.register(DriverCoupon, DriverCouponAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(PassengerReturn, PassengerReturnAdmin)
admin.site.register(DriverReturn, DriverReturnAdmin)
