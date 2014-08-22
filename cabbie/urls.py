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

#router.register(r'users', import_('cabbie.apps.account.views.UserViewSet'))
router.register(r'passengers',
                import_('cabbie.apps.account.views.PassengerViewSet'))
router.register(r'drivers',
                import_('cabbie.apps.account.views.DriverViewSet'))
router.register(r'rides',
                import_('cabbie.apps.drive.views.RideViewSet'))

urlpatterns += patterns('',
    url(r'^api/drivers/verify',
        import_('cabbie.apps.account.views.DriverVerifyView').as_view()),
)
urlpatterns += patterns('',
    url(r'^api/drivers/accept',
        import_('cabbie.apps.account.views.DriverAcceptView').as_view()),
)
urlpatterns += patterns('',
    url(r'^api/auth',
        import_('cabbie.apps.account.views.ObtainAuthToken').as_view()),
)

urlpatterns += patterns('',
    url(r'^api/', include(router.urls)),
)


# App
# ---

urlpatterns += patterns('',
    url(r'^_/drive/', include('cabbie.apps.drive.urls')),
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
