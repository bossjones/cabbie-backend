# encoding: utf8

from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AdminTextareaWidget

from cabbie.apps.affiliation.models import Affiliation
from cabbie.common.admin import AbstractAdmin, DateRangeFilter

class AffiliationAdmin(AbstractAdmin):
    deletable = True
    list_display = ('id', 'name', 'company_code', 'affiliated_at', 'certificate_code', 'ride_mileage',
                    'event_start_at', 'event_end_at', 'is_active',
                    'updated_at', 'created_at',) 
    ordering = ('-created_at',)
    search_fields = (
        'name', 'company_code'
    )
    readonly_fields = ('certificate_code',)

    fieldsets = (
        (None, {
            'fields': ('name', 'company_code', 'affiliated_at', 'ride_mileage', 'event_start_at', 'event_end_at', 'is_active'),
        }), 
        ('읽기전용', {
            'fields': ('certificate_code',),
        }),
    )
    
    actions = (
        'activate',
        'inactivate',
    )

    def activate(self, request, queryset):
        affiliations = list(queryset.all())
        for affiliation in affiliations:
            affiliation.activate()
        msg = u'{0}개의 제휴사를 활성화처리 하였습니다.'.format(len(affiliations))
        self.message_user(request, msg)
    activate.short_description = u'활성화'

    def inactivate(self, request, queryset):
        affiliations = list(queryset.all())
        for affiliation in affiliations:
            affiliation.inactivate()
        msg = u'{0}개의 제휴사를 비활성화처리 하였습니다.'.format(len(affiliations))
        self.message_user(request, msg)
    inactivate.short_description = u'비활성화'


admin.site.register(Affiliation, AffiliationAdmin)
