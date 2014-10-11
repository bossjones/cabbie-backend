from django.contrib import admin

from cabbie.apps.account.models import Driver, Passenger


class DriverAdmin(admin.ModelAdmin):
    list_display = ('phone', 'name', 'deposit', 'point', 'license_number', 'car_number',
                    'company', 'bank_account', 'verification_code',
                    'is_verified', 'is_accepted', 'is_freezed', 'date_joined')
    fields = ('phone', 'name', 'license_number', 'car_number', 'company',
              'bank_account', 'image')
    ordering = ('-date_joined',)

    actions = (
        'send_verification_code',
        'freeze',
        'unfreeze',
    )

    def send_verification_code(self, request, queryset):
        for driver in queryset.all():
            driver.send_verification_code()

    def freeze(self, request, queryset):
        for driver in queryset.all():
            driver.freeze()

    def unfreeze(self, request, queryset):
        for driver in queryset.all():
            driver.unfreeze()


class PassengerAdmin(admin.ModelAdmin):
    list_display = ('phone', 'name', 'email', 'point', 'ride_count',
                    'date_joined')
    fields = ('phone', 'password', 'name', 'email')
    ordering = ('-date_joined',)

admin.site.register(Driver, DriverAdmin)
admin.site.register(Passenger, PassengerAdmin)
