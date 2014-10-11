# encoding: utf8

from django.contrib import admin

from cabbie.apps.stats.models import LocationDataAccess, LocationDataProvide


class LocationDataAccessAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at_')

    def created_at_(self, obj):
        return obj.created_at

    created_at_.short_description = u'접근시간'

class LocationDataProvideAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'created_at_')

    def created_at_(self, obj):
        return obj.created_at

    created_at_.short_description = u'제공시간'

admin.site.register(LocationDataAccess, LocationDataAccessAdmin)
admin.site.register(LocationDataProvide, LocationDataProvideAdmin)
