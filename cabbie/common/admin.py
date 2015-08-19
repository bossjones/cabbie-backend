from daterange_filter.filter import DateRangeFilter as BaseDateRangeFilter
from django.db import models
from django.contrib import admin
from django.forms import CheckboxSelectMultiple
from import_export.admin import ExportMixin


class AbstractAdmin(ExportMixin, admin.ModelAdmin):
    deletable = False
    addable = True

    actions_on_top = True
    actions_on_bottom = False 

    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }

    def get_actions(self, request):
        actions = super(AbstractAdmin, self).get_actions(request)
        if not self.deletable and 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        return self.deletable

    def has_add_permission(self, request, obj=None):
        return self.addable


class DateRangeFilter(BaseDateRangeFilter):
    template = 'admin/daterange_filter.html'
