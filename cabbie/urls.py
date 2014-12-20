from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from rest_framework import routers

from cabbie.common.forms import AdminAuthenticationForm
from cabbie.utils.importlib import import_class as import_


urlpatterns = patterns('')


# Admin
# -----

admin.site.login_form = AdminAuthenticationForm

# unregister django group admin
admin.site.unregister(import_('django.contrib.auth.models.Group'))

# unregister authtoken admin
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
admin.site.unregister(import_('cabbie.apps.payment.models.Transaction'))
admin.site.unregister(import_('cabbie.apps.payment.models.PassengerReturn'))
admin.site.unregister(import_('cabbie.apps.payment.models.DriverReturn'))

# unregister recommend admin
admin.site.unregister(import_('cabbie.apps.recommend.models.Recommend'))

# unregister hotspot, favorite admin
admin.site.unregister(import_('cabbie.apps.drive.models.Favorite'))
admin.site.unregister(import_('cabbie.apps.drive.models.Hotspot'))

admin.autodiscover()
urlpatterns += patterns('',
    (r'^admin/', include(admin.site.urls)),
)


# REST
# ----

router = routers.DefaultRouter(trailing_slash=False)

router.register(r'passengers',
                import_('cabbie.apps.account.views.PassengerViewSet'))
router.register(r'drivers/bills',
                import_('cabbie.apps.payment.views.DriverBillViewSet'))
router.register(r'drivers/coupon',
                import_('cabbie.apps.payment.views.DriverCouponViewSet'))
router.register(r'drivers/stats/month',
                import_('cabbie.apps.stats.views.DriverRideStatMonthViewSet'))
router.register(r'drivers/stats/week',
                import_('cabbie.apps.stats.views.DriverRideStatWeekViewSet'))
router.register(r'drivers/stats/day',
                import_('cabbie.apps.stats.views.DriverRideStatDayViewSet'))
router.register(r'drivers',
                import_('cabbie.apps.account.views.DriverViewSet'))
router.register(r'rides',
                import_('cabbie.apps.drive.views.RideViewSet'))
router.register(r'favorites',
                import_('cabbie.apps.drive.views.FavoriteViewSet'))
router.register(r'hotspots',
                import_('cabbie.apps.drive.views.HotspotViewSet'))
router.register(r'transactions',
                import_('cabbie.apps.payment.views.TransactionViewSet'))
router.register(r'recommends',
                import_('cabbie.apps.recommend.views.RecommendViewSet'))

urlpatterns += patterns('',
    url(r'^api/passengers/signup',
        import_('cabbie.apps.account.views.PassengerSignupView').as_view(),
            name='api-passengers-signup'),
    url(r'^api/drivers/verify',
        import_('cabbie.apps.account.views.DriverVerifyView').as_view()),
    url(r'^api/drivers/accept',
        import_('cabbie.apps.account.views.DriverAcceptView').as_view()),
    url(r'^api/drivers/upload/profile_photo',
        import_('cabbie.apps.account.views.DriverPhotoUploadView').as_view()),
    url(r'^api/recommends/query',
        import_('cabbie.apps.recommend.views.RecommendQueryView').as_view()),
    url(r'^api/phone/verify/issue/?$',
        import_('cabbie.apps.account.views.PhoneVerifyIssueView').as_view()),
    url(r'^api/phone/verify/check/?$',
        import_('cabbie.apps.account.views.PhoneVerifyCheckView').as_view()),

    url(r'^api/user/password_reset/activate',
        import_('cabbie.apps.account.views.PasswordResetActivateView').as_view()),
    url(r'^api/user/password_reset',
        import_('cabbie.apps.account.views.PasswordResetView').as_view()),
    url(r'^api/user/query',
        import_('cabbie.apps.account.views.UserQueryView').as_view()),
    url(r'^api/user/dropout',
        import_('cabbie.apps.account.views.UserDropoutView').as_view()),
    url(r'^api/geo/poi/around',
        import_('cabbie.apps.drive.views.GeoPOIAroundView').as_view()),
    url(r'^api/geo/poi',
        import_('cabbie.apps.drive.views.GeoPOIView').as_view()),
    url(r'^api/geo/reverse',
        import_('cabbie.apps.drive.views.GeoReverseView').as_view()),

    url(r'^api/auth',
        import_('cabbie.apps.account.views.ObtainAuthToken').as_view()),

    url(r'^api/appversion/android/driver',
        import_('cabbie.apps.appversion.views.AndroidDriverView').as_view()),

    url(r'^api/drivers/reserve',
        import_('cabbie.apps.account.views.DriverReserveView').as_view()),

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
