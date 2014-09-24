from django.contrib import admin

from cabbie.apps.payment.models import DriverBill, DriverCoupon, Transaction


class DriverBillAdmin(admin.ModelAdmin):
    list_display = ('driver', 'target_month', 'amount', 'created_at')
    fields = ('driver', 'target_month', 'amount')


class DriverCouponAdmin(admin.ModelAdmin):
    list_display = ('driver', 'coupon_type', 'amount', 'serial_number',
                    'created_at')
    fields = ('driver', 'coupon_type', 'amount', 'serial_number')


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user_', 'transaction_type', 'amount', 'note',
                    'created_at')
    fields = ('user_content_type', 'user_object_id', 'transaction_type',
              'amount', 'note',)

    def user_(self, obj):
        return obj.user


admin.site.register(DriverBill, DriverBillAdmin)
admin.site.register(DriverCoupon, DriverCouponAdmin)
admin.site.register(Transaction, TransactionAdmin)
