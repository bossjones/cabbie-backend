from django.contrib import admin

from cabbie.apps.drive.models import Ride, RideHistory, Favorite


class RideAdmin(admin.ModelAdmin):
    list_display = ('passenger', 'driver', 'state', 'source',
                    'source_location', 'destination', 'destination_location',
                    'rating', 'comment', 'updated_at', 'created_at')


class RideHistoryAdmin(admin.ModelAdmin):
    list_display = ('ride', 'driver', 'state', 'passenger_location',
                    'driver_location', 'created_at')


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('passenger', 'name', 'location', 'address', 'poi',
                    'created_at')


admin.site.register(Ride, RideAdmin)
admin.site.register(RideHistory, RideHistoryAdmin)
admin.site.register(Favorite, FavoriteAdmin)
