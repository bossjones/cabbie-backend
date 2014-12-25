from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.http import HttpResponseRedirect 
from rest_framework import routers

from cabbie.common.forms import AdminAuthenticationForm
from cabbie.utils.importlib import import_class as import_
from cabbie.apps.index.views import index

urlpatterns = patterns('')


# Admin
# -----

admin.site.login_form = AdminAuthenticationForm

# unregister django group admin
if not settings.DEBUG:
    admin.site.unregister(import_('django.contrib.auth.models.Group'))

# unregister authtoken admin
if not settings.DEBUG:
    admin.site.unregister(import_('rest_framework.authtoken.models.Token'))

# unregister django celery admin
admin.site.unregister(import_('djcelery.models.CrontabSchedule'))
admin.site.unregister(import_('djcelery.models.IntervalSchedule'))
admin.site.unregister(import_('djcelery.models.PeriodicTask'))
admin.site.unregister(import_('djcelery.models.TaskState'))
admin.site.unregister(import_('djcelery.models.WorkerState'))

# unregister django ses admin
admin.site.unregister(import_('django_ses.models.SESStat'))

# unregister payment admin
admin.site.unregister(import_('cabbie.apps.payment.models.DriverBill'))
admin.site.unregister(import_('cabbie.apps.payment.models.DriverCoupon'))
admin.site.unregister(import_('cabbie.apps.payment.models.DriverReturn'))

# unregister recommend admin
admin.site.unregister(import_('cabbie.apps.recommend.models.Recommend'))

# unregister hotspot, favorite admin
admin.site.unregister(import_('cabbie.apps.drive.models.Favorite'))
admin.site.unregister(import_('cabbie.apps.drive.models.Hotspot'))

admin.autodiscover()
urlpatterns += patterns('',
    (r'^tinymce/', include('tinymce.urls')),
    (r'^$', lambda r: HttpResponseRedirect('admin/')),
    (r'^admin/', include(admin.site.urls)),
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

    # add toolbar setting 
    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )
