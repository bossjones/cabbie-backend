# encoding: utf8

from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AdminTextareaWidget

from cabbie.apps.account.models import (
    User, Driver, Passenger, DriverReservation, PassengerDropout,
    DriverDropout)
from cabbie.common.admin import AbstractAdmin, DateRangeFilter


def rating_round_off(obj):
    return "%.3f" % (obj.rating)
rating_round_off.short_description = u'평점'


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
    list_max_show_all = 1000

    form = DriverForm
    ordering = ('-date_joined',)
    list_display = ('id', 'phone', 'name', 'profile_image_link', 'app_version', 'taxi_type', 'car_number', 'province', 'region', 'car_model', 'company',
                    rating_round_off, 'rating_kindness', 'rating_cleanliness', 'rating_security', 
                    'ride_count', 'total_ride_count',
                    'verification_code', 'is_verification_code_notified', 'is_verified', 'is_accepted',
                    'is_sms_agreed',
                    'is_freezed', 
                    'is_educated', 'education',
                    'date_joined',
                    'link_to_rides')
    fieldsets = (
        (None, {
            'fields': (
                'phone', 'name', 'license_number', 'car_number', 'province', 'region', 'car_model',
                'company', 'bank_account', 'max_capacity',
                'taxi_type', 'is_educated', 'education', 'about', 'image',
            ),
        }),
        ('읽기전용', {
            'fields': (
                'recommend_code', 'point', rating_round_off, 'rating_kindness', 'rating_cleanliness', 'rating_security',
                'ride_count', 'total_ride_count',
                'verification_code', 'is_verified', 'is_accepted',
                'is_freezed', 'date_joined',
                'last_active_at',
            ),
        }),
    )
    search_fields = (
        'phone', 'name', '=id', 'car_model', 'education__name',
    )
    readonly_fields = (
        'recommend_code', 'point', rating_round_off, 'rating_kindness', 'rating_cleanliness', 'rating_security',
        'ride_count', 'total_ride_count',
        'verification_code', 'is_verified', 'is_accepted',
        'is_freezed', 'date_joined',
        'last_active_at',
    )
    list_filter = (
        'app_version',
        'taxi_type',
        'is_verified',
        'is_accepted',
        'is_freezed',
        'is_educated',
        'province',
        'region',
        'education',
        ('date_joined', DateRangeFilter),
    )

    actions = (
        'send_verification_code',
        'mark_as_educated',
        'mark_as_uneducated',
        'freeze',
        'unfreeze',
        'force_verify',
        'force_accept',
        'clear_image',
        'dropout',
    )

    def send_verification_code(self, request, queryset):
        drivers = list(queryset.all())
        for driver in drivers:
            driver.send_verification_code()
            driver.is_verification_code_notified = True
            driver.save(update_fields=['is_verification_code_notified'])
        msg = u'{0}명의 기사에게 인증코드가 전송되었습니다.'.format(
            len(drivers))
        self.message_user(request, msg)
    send_verification_code.short_description = u'인증코드 전송'

    def mark_as_educated(self, request, queryset):
        drivers = list(queryset.all())
        for driver in drivers:
            driver.mark_as_educated()
        msg = u'{0}명의 기사가 교육이수로 처리되었습니다.'.format(len(drivers))
        self.message_user(request, msg)
    mark_as_educated.short_description = u'교육이수'

    def mark_as_uneducated(self, request, queryset):
        drivers = list(queryset.all())
        for driver in drivers:
            driver.mark_as_educated(False)
        msg = u'{0}명의 기사가 교육이수에서 해제되었습니다.'.format(len(drivers))
        self.message_user(request, msg)
    mark_as_uneducated.short_description = u'교육이수 해제'


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

    def clear_image(self, request, queryset):
        drivers = list(queryset.all())
        for driver in drivers:
            driver.clear_image()
        msg = u'{0}명의 기사의 프로필 사진을 삭제하였습니다.'.format(len(drivers)) 
        self.message_user(request, msg)
    clear_image.short_description = u'프로필사진 삭제'

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
    list_max_show_all = 1000

    ordering = ('-date_joined',)
    list_display = ('id', 'phone', 'email', 'name', 'app_version', 'point',
                    'is_sms_agreed', 'is_email_agreed',
                    'total_ride_count',
                    'date_joined', 'link_to_rides')
    fieldsets = (
        (None, {
            'fields': (
                'phone', 'name', 'bank_account', 'email',
            ),
        }),
        ('읽기전용', {
            'fields': (
                'recommend_code', 'point', 'total_ride_count',
            ),
        }),
    )
    search_fields = (
        'phone', 'name', '=email', '=id',
    )
    readonly_fields = (
        'recommend_code', 'point', 'total_ride_count',
    )
    list_filter = (
        'app_version',
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
    deletable = True

    form = DriverReservationAdminForm
    list_display = ('phone', 'name', 'car_model', 'is_joined', 'created_at', 'cert_image_link')
    fields = ('phone', 'name', 'car_model')
    ordering = ('-created_at',)
    actions = ('join',)
    search_fields = (
        'phone', 'name', '=id',
    )
    list_filter = (
        'is_joined',
    )

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
