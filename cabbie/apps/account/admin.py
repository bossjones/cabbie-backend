# encoding: utf8

from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AdminTextareaWidget

from cabbie.apps.account.models import (
    User, Driver, Passenger, DriverReservation, PassengerDropout,
    DriverDropout)
from cabbie.common.admin import AbstractAdmin, DateRangeFilter


class StaffAdmin(AbstractAdmin):
    list_display = ('id', 'phone', 'name', 'is_superuser', 'date_joined')
    list_filter = (
        ('is_staff', admin.BooleanFieldListFilter),
    )
    search_fields = (
        '=id',
        '^phone',
        'name',
    )
    fields = ('phone', 'name', 'password')
    ordering = ('-date_joined',)

    def get_queryset(self, request):
        qs = self.model._default_manager.get_queryset()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        # only staff
        # qs = qs.filter(is_staff=True)
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


class DriverAdmin(AbstractAdmin):
    form = DriverForm
    ordering = ('-date_joined',)
    list_display = ('phone', 'name', 'taxi_type', 'car_number', 'company',
                    'garage', 'point', 'rating', 'current_month_board_count',
                    'previous_month_board_count', 'board_count',
                    'verification_code', 'is_verified', 'is_accepted',
                    'is_freezed', 'is_super', 'is_dormant', 'date_joined',
                    'link_to_rides')
    fieldsets = (
        (None, {
            'fields': (
                'phone', 'name', 'license_number', 'car_number', 'car_model',
                'company', 'garage', 'bank_account', 'max_capacity',
                'taxi_type', 'taxi_service', 'about', 'image',
            ),
        }),
        ('읽기전용', {
            'fields': (
                'recommend_code', 'point', 'rating',
                'current_month_board_count', 'previous_month_board_count',
                'board_count', 'passenger_recommend_count',
                'driver_recommend_count', 'recommended_count',
                'verification_code', 'is_verified', 'is_accepted',
                'is_freezed', 'is_super', 'is_dormant', 'date_joined',
                'last_active_at',
            ),
        }),
    )
    search_fields = (
        '^phone', 'name', '=id',
    )
    readonly_fields = (
        'recommend_code', 'point', 'rating', 'current_month_board_count',
        'previous_month_board_count', 'board_count',
        'passenger_recommend_count', 'driver_recommend_count',
        'recommended_count', 'verification_code', 'is_verified', 'is_accepted',
        'is_freezed', 'is_super', 'is_dormant', 'date_joined',
        'last_active_at',
    )
    list_filter = (
        'taxi_type',
        'is_verified',
        'is_accepted',
        'is_freezed',
        'is_super',
        'is_dormant',
        ('date_joined', DateRangeFilter),
    )

    actions = (
        'send_verification_code',
        'freeze',
        'unfreeze',
        'force_verify',
        'force_accept',
        'dropout',
    )

    def send_verification_code(self, request, queryset):
        drivers = list(queryset.all())
        for driver in drivers:
            driver.send_verification_code()
        msg = u'{0}명의 기사에게 인증코드가 전송되었습니다.'.format(
            len(drivers))
        self.message_user(request, msg)
    send_verification_code.short_description = u'인증코드 전송'

    def freeze(self, request, queryset):
        drivers = list(queryset.all())
        for driver in drivers:
            driver.freeze()
        msg = u'{0}명의 기사가 사용제한 설정되었습니다.'.format(
            len(drivers))
        self.message_user(request, msg)
    freeze.short_description = u'사용제한 설정'

    def unfreeze(self, request, queryset):
        drivers = list(queryset.all())
        for driver in drivers:
            driver.unfreeze()
        msg = u'{0}명의 기사가 사용제한 해제되었습니다.'.format(
            len(drivers))
        self.message_user(request, msg)
    unfreeze.short_description = u'사용제한 해제'

    def force_verify(self, request, queryset):
        drivers = list(queryset.all())
        for driver in drivers:
            driver.is_verified = True
            driver.save(update_fields=['is_verified'])
        msg = u'{0}명의 기사가 인증 처리되었습니다.'.format(
            len(drivers))
        self.message_user(request, msg)
    force_verify.short_description = u'인증 처리'

    def force_accept(self, request, queryset):
        drivers = list(queryset.all())
        for driver in drivers:
            driver.is_accepted = True
            driver.save(update_fields=['is_accepted'])
        msg = u'{0}명의 기사가 약관동의 처리되었습니다.'.format(
            len(drivers))
        self.message_user(request, msg)
    force_accept.short_description = u'약관동의 처리'

    def dropout(self, request, queryset):
        drivers = list(queryset.all())
        for driver in drivers:
            driver.dropout(DriverDropout.ADMIN)
        msg = u'{0}명의 기사가 탈퇴 처리되었습니다.'.format(len(drivers))
        self.message_user(request, msg)
    dropout.short_description = u'탈퇴 처리'

    def link_to_rides(self, obj):
        url = u'/admin/drive/ride/?driver_id={0}'.format(obj.id)
        return u'<a href="{0}">조회</a>'.format(url)
    link_to_rides.short_description = u'배차이력'
    link_to_rides.allow_tags = True


class PassengerAdmin(AbstractAdmin):
    ordering = ('-date_joined',)
    list_display = ('phone', 'email', 'name', 'point',
                    'current_month_board_count', 'previous_month_board_count',
                    'board_count', 'passenger_recommend_count',
                    'recommended_count', 'date_joined', 'link_to_rides')
    fieldsets = (
        (None, {
            'fields': (
                'phone', 'name', 'bank_account', 'email',
            ),
        }),
        ('읽기전용', {
            'fields': (
                'recommend_code', 'point', 'current_month_board_count',
                'previous_month_board_count', 'board_count',
                'passenger_recommend_count', 'recommended_count'
            ),
        }),
    )
    search_fields = (
        '^phone', 'name', '=email', '=id',
    )
    readonly_fields = (
        'recommend_code', 'point', 'current_month_board_count',
        'previous_month_board_count', 'board_count',
        'passenger_recommend_count', 'recommended_count'
    )
    list_filter = (
        ('date_joined', DateRangeFilter),
    )
    actions = (
        'dropout',
    )

    def dropout(self, request, queryset):
        passengers = list(queryset.all())
        for passenger in passengers:
            passenger.dropout(PassengerDropout.ADMIN)
        msg = u'{0}명의 승객이 탈퇴 처리되었습니다.'.format(len(passengers))
        self.message_user(request, msg)
    dropout.short_description = u'탈퇴 처리'

    def link_to_rides(self, obj):
        url = u'/admin/drive/ride/?passenger_id={0}'.format(obj.id)
        return u'<a href="{0}">조회</a>'.format(url)
    link_to_rides.short_description = u'배차이력'
    link_to_rides.allow_tags = True


class DriverReservationAdminForm(forms.ModelForm):
    class Meta:
        model = DriverReservation
        widgets = {
            'is_joined': forms.CheckboxInput()
        }


class DriverReservationAdmin(AbstractAdmin):
    form = DriverReservationAdminForm
    list_display = ('phone', 'name', 'is_joined', 'created_at')
    fields = ('phone', 'name')
    ordering = ('-created_at',)
    actions = ('join',)

    def join(self, request, queryset):
        drivers = list(queryset.all())
        for driver in drivers:
            driver.join()
        msg = u'{0}명의 기사가 가입 처리되었습니다.'.format(
            len(drivers))
        self.message_user(request, msg)
    join.short_description = u'가입처리'


class AbstractDropoutAdmin(AbstractAdmin):
    addable = False
    list_display = ('user_id', 'dropout_type', 'note', 'created_at')
    ordering = ('-created_at',)


class PassengerDropoutAdmin(AbstractDropoutAdmin):  pass
class DriverDropoutAdmin(AbstractDropoutAdmin):     pass


admin.site.register(User, StaffAdmin)
admin.site.register(Driver, DriverAdmin)
admin.site.register(Passenger, PassengerAdmin)
admin.site.register(DriverReservation, DriverReservationAdmin)
admin.site.register(PassengerDropout, PassengerDropoutAdmin)
admin.site.register(DriverDropout, DriverDropoutAdmin)
