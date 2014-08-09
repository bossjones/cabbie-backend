from django.conf.urls import patterns, url

from cabbie.apps.drive.views import (
    InternalRideCreateView, InternalRideUpdateView)


urlpatterns = patterns('',
    url('^ride/create/?$', InternalRideCreateView.as_view(),
        name='internal_ride_create'),
    url('^ride/(?P<pk>\d+)/update/?$', InternalRideUpdateView.as_view(),
        name='internal_ride_update'),
)
