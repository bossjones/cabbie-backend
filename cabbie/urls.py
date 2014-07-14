from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from rest_framework import routers

from cabbie.utils.importlib import import_class as import_


urlpatterns = patterns('')


# Admin
# -----

admin.autodiscover()
urlpatterns += patterns('',
    (r'^admin/', include(admin.site.urls)),
)


# REST
# ----

router = routers.DefaultRouter(trailing_slash=False)

router.register(r'users', import_('cabbie.apps.account.views.UserViewSet'))

urlpatterns += patterns('',
    url(r'^api/', include(router.urls)),
)

urlpatterns += patterns('',
    url(r'^api/auth/', 'rest_framework.authtoken.views.obtain_auth_token')
)


# App
# ---

urlpatterns += patterns('',
    url('', include('cabbie.apps.account.urls')),
)


# Local development
# -----------------

if settings.DEBUG:
    urlpatterns += patterns('django.views.static',
        url(r'^(?P<path>(js|css|less|images|components|bower_components)/.+)$',
            'serve', {'document_root': settings.STATIC_DIR}),
        url(r'^media/(?P<path>.+)$', 'serve',
            {'document_root': settings.MEDIA_DIR}),
    )
