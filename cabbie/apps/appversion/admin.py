from django.contrib import admin

from cabbie.apps.appversion.models import AndroidDriver, AndroidPassenger

class AndroidDriverAdmin(admin.ModelAdmin):
    list_display = ('version_code', 'version_name', 'is_update_required', 'description')
    fields = ('version_code', 'version_name', 'is_update_required', 'description' )

class AndroidPassengerAdmin(admin.ModelAdmin):
    list_display = ('version_code', 'version_name', 'is_update_required', 'description')
    fields = ('version_code', 'version_name', 'is_update_required', 'description' )


admin.site.register(AndroidDriver, AndroidDriverAdmin)
admin.site.register(AndroidPassenger, AndroidPassengerAdmin)
