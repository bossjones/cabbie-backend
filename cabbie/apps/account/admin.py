# encoding: utf8

from django import forms, template

from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib import admin
from django.contrib.admin.widgets import AdminTextareaWidget

from cabbie.apps.account.models import (
    User, Driver, Passenger, DriverReservation, PassengerDropout,
    DriverDropout)
from cabbie.apps.account.forms import EducationSelectForm
from cabbie.apps.account.filter import EndDateIncludingDateRangeFilter
from cabbie.apps.payment.models import PassengerReturn
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
            'remark': AdminTextareaWidget(),
        }


class DriverAdmin(AbstractAdmin):
    list_max_show_all = 1000

    form = DriverForm
    ordering = ('-date_joined',)
    list_display = ('id', 'phone', 'name', 'profile_image_link', 'app_version', 'car_number', 'province', 'region', 'car_model', 
                    rating_round_off, 'rating_kindness', 'rating_cleanliness', 'rating_security', 
                    'ride_count', 'total_ride_count',
                    'verification_code', 'is_verification_code_notified', 'is_verified', 'is_accepted',
                    'is_sms_agreed',
                    'is_freezed', 
                    'is_educated', 'education',
                    'remark',
                    'date_joined',
                    'link_to_rides')
    fieldsets = (
        (None, {
            'fields': (
                'phone', 'name', 'license_number', 'car_number', 'province', 'region', 'car_model',
                'bank_account', 
                'is_educated', 'education', 'about', 'image',
                'remark',
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
        'phone', 'name', '=id', 'car_model', 'car_number', 'license_number', 'education__name',
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
        'is_verified',
        'is_accepted',
        'is_sms_agreed',
        'is_freezed',
        'is_educated',
        'province',
        'region',
        'education',
        'remark',
        ('date_joined', EndDateIncludingDateRangeFilter),
    )

    actions = (
        'send_verification_code',
        'mark_as_educated',
        'mark_as_uneducated',
        'freeze',
        'unfreeze',
        'force_verify',
        'force_accept',
        'force_sms_agree',
        'force_sms_disagree',
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
        msg = u'{0}명의 기사가 승인 처리되었습니다.'.format(
            len(drivers))
        self.message_user(request, msg)
    force_accept.short_description = u'승인 처리'

    def force_sms_agree(self, request, queryset):
        drivers = list(queryset.all())
        for driver in drivers:
            driver.is_sms_agreed = True
            driver.save(update_fields=['is_sms_agreed'])
        msg = u'{0}명의 기사가 SMS 수신동의 처리되었습니다.'.format(
            len(drivers))
        self.message_user(request, msg)
    force_sms_agree.short_description = u'SMS 수신동의 처리'

    def force_sms_disagree(self, request, queryset):
        drivers = list(queryset.all())
        for driver in drivers:
            driver.is_sms_agreed = False 
            driver.save(update_fields=['is_sms_agreed'])
        msg = u'{0}명의 기사가 SMS 수신동의 해제되었습니다.'.format(
            len(drivers))
        self.message_user(request, msg)
    force_sms_disagree.short_description = u'SMS 수신동의 해제'

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
            note = u'{name} {province}'.format(name=driver.name, province=driver.province)
            
            if driver.region:
                note += u' {region}'.format(region=driver.region)

            driver.dropout(DriverDropout.ADMIN, note=note)
        msg = u'{0}명의 기사가 탈퇴 처리되었습니다.'.format(len(drivers))
        self.message_user(request, msg)
    dropout.short_description = u'탈퇴 처리'

    def link_to_rides(self, obj):
        url = u'/admin/drive/ride/?driver_id={0}'.format(obj.id)
        return u'<a href="{0}">조회</a>'.format(url)
    link_to_rides.short_description = u'배차이력'
    link_to_rides.allow_tags = True

    def mark_as_educated(self, request, queryset):
        form = None

        if 'apply' in request.POST:
            form = EducationSelectForm(request.POST)

            if form.is_valid():
                education = form.cleaned_data['education']

                drivers = list(queryset.all())
                for driver in drivers:
                    driver.mark_as_educated(education)

                msg = u'{0}명의 기사가 {1}(으)로 교육이수 처리되었습니다.'.format(len(drivers), education)
                self.message_user(request, msg)
    
                return HttpResponseRedirect(request.get_full_path())

        if not form:
            form = EducationSelectForm(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME) })

        opts = self.model._meta
        app_label = opts.app_label

        return render_to_response(
            'admin/education_selection.html',
            {'drivers': queryset, 'education_selection_form': form, 'opts': opts, 'app_label': app_label},
            context_instance=template.RequestContext(request)
        )
    mark_as_educated.short_description = u'교육이수 처리'

    def mark_as_uneducated(self, request, queryset):
        drivers = list(queryset.all())
        for driver in drivers:
            driver.mark_as_uneducated()
            
        msg = u'{0}명의 기사가 교육이수에서 해제되었습니다.'.format(len(drivers))
        self.message_user(request, msg)
    mark_as_uneducated.short_description = u'교육이수 해제'


class PassengerReturnInline(admin.TabularInline):
    model = PassengerReturn
    extra = 0


class PassengerAdmin(AbstractAdmin):
    inlines = [
        PassengerReturnInline,
    ]
    list_max_show_all = 1000

    ordering = ('-date_joined',)
    list_display = ('id', 'phone', 'device_type_kor', 'email', 'name', 'recommend_code', 'cu_event', 'affiliation', 'app_version', 'point',
                    'is_sms_agreed', 'is_email_agreed',
                    'total_ride_count',
                    'date_joined', 'link_to_rides')
    fieldsets = (
        (None, {
            'fields': (
                'phone', 'name', 'bank_account', 'email', 'affiliation',
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
        'affiliation',
        ('date_joined', EndDateIncludingDateRangeFilter),
    )
    actions = (
        'dropout',
    )

    def dropout(self, request, queryset):
        passengers = list(queryset.all())
        for passenger in passengers:
            note = u'{name} {phone}'.format(name=passenger.name, phone=passenger.phone)

            passenger.dropout(PassengerDropout.ADMIN, note=note)
        msg = u'{0}명의 승객이 탈퇴 처리되었습니다.'.format(len(passengers))
        self.message_user(request, msg)
    dropout.short_description = u'탈퇴 처리'

    def link_to_rides(self, obj):
        url = u'/admin/drive/ride/?passenger_id={0}'.format(obj.id)
        return u'<a href="{0}">조회</a>'.format(url)
    link_to_rides.short_description = u'배차이력'
    link_to_rides.allow_tags = True

    def device_type_kor(self, obj):
        if obj.device_type == 'a': 
            return u'안드로이드'
        elif obj.device_type == 'i': 
            return u'아이폰'
        else: 
            return u''
    device_type_kor.short_description = u'기기'
    
    def cu_event(self, obj):
        if obj.cu_event:
            ret = u'{code}'.format(code=obj.cu_event.code)
            if obj.cu_event.is_gift_sent:
                ret += u'(G)'
            return ret 
        else:
            return ''


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
    deletable = True
    list_display = ('user_id', 'dropout_type', 'note', 'created_at')
    ordering = ('-created_at',)
    list_filter = ('dropout_type',)
    search_fields = ('note',)


class PassengerDropoutAdmin(AbstractDropoutAdmin):  pass
class DriverDropoutAdmin(AbstractDropoutAdmin):     pass


admin.site.register(User, StaffAdmin)
admin.site.register(Driver, DriverAdmin)
admin.site.register(Passenger, PassengerAdmin)
admin.site.register(DriverReservation, DriverReservationAdmin)
admin.site.register(PassengerDropout, PassengerDropoutAdmin)
admin.site.register(DriverDropout, DriverDropoutAdmin)
