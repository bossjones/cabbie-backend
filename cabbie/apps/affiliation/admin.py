# encoding: utf8

from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AdminTextareaWidget

from cabbie.apps.affiliation.models import Affiliation
from cabbie.common.admin import AbstractAdmin, DateRangeFilter

class AffiliationAdmin(AbstractAdmin):
    list_display = ('id', 'name', 'certificate_code', 'ride_mileage',
                    'updated_at', 'created_at',) 
    ordering = ('-created_at',)
    search_fields = (
        'name',
    )
    readonly_fields = ('certificate_code',)

    fieldsets = (
        (None, {
            'fields': ('name', 'ride_mileage',),
        }), 
        ('읽기전용', {
            'fields': ('certificate_code',),
        }),
    )

admin.site.register(Affiliation, AffiliationAdmin)
