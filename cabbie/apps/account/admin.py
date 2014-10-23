from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AdminTextareaWidget

from cabbie.apps.account.models import User, Driver, Passenger, DriverReservation

class StaffAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'is_superuser', 'date_joined')

    list_filter = (
        ('is_staff', admin.BooleanFieldListFilter),
    )

    fields = ('name', 'phone', 'password') 

    ordering = ('-date_joined',)

    def get_queryset(self, request):
        qs = self.model._default_manager.get_queryset()
        
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        # only staff
        qs = qs.filter(is_staff=True)
        return qs

    def save_model(self, request, obj, form, change):
        # force staff
        obj.is_staff = True
        obj.save()

class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        widgets = {
            'about': AdminTextareaWidget(),
        }


class DriverAdmin(admin.ModelAdmin):
    form = DriverForm
    list_display = ('phone', 'name', 'deposit', 'point', 'license_number',
                    'car_number', 'company', 'bank_account', 'rating',
                    'verification_code', 'is_verified', 'is_accepted',
                    'is_freezed', 'date_joined')
    fields = ('phone', 'name', 'license_number', 'car_number', 'car_model',
              'company', 'bank_account', 'max_capacity', 'taxi_type',
              'taxi_service', 'about', 'image')
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

class DriverReservationAdminForm(forms.ModelForm):
    class Meta:
        model = DriverReservation
        widgets = {
            'is_joined':forms.CheckboxInput()
        }

class DriverReservationAdmin(admin.ModelAdmin):
    form = DriverReservationAdminForm

    list_display = ('phone', 'name', 'is_joined', 'created_at')
    fields = ('phone', 'name')
    ordering = ('-created_at',)

    actions = ('join',)
    
    def join(self, request, queryset):
        for driver in queryset.all():
            driver.join()


admin.site.register(User, StaffAdmin)
admin.site.register(Driver, DriverAdmin)
admin.site.register(Passenger, PassengerAdmin)
admin.site.register(DriverReservation, DriverReservationAdmin)
