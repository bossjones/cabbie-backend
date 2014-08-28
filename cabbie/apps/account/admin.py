from django.contrib import admin

from cabbie.apps.account.models import Driver


class DriverAdmin(admin.ModelAdmin):
    list_display = ('phone', 'name', 'license_number', 'car_number', 'company', 'bank_account', 'verification_code',
                    'is_verified', 'is_accepted', 'date_joined')
    fields = ('phone', 'name', 'license_number', 'car_number', 'company', 'bank_account')
    ordering = ('-date_joined',)

    actions = (
        'send_verification_code',
    )

    def send_verification_code(self, request, queryset):
        for driver in queryset.all():
            driver.send_verification_code()


admin.site.register(Driver, DriverAdmin)
