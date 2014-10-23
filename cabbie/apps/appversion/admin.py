from django.contrib import admin

from cabbie.apps.appversion.models import AndroidDriver

class AndroidDriverAdmin(admin.ModelAdmin):
    list_display = ('version_code', 'version_name', 'is_update_required', 'description')

admin.site.register(AndroidDriver, AndroidDriverAdmin)
