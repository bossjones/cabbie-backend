# -*- coding: utf-8 -*-

"""
Django settings for `cabbie` project.
"""

import os

from celery.schedules import crontab
import djcelery


# Django settings
# ===============

DEBUG = False
TEMPLATE_DEBUG = False
SECRET_KEY = '3bh%kzi)gd)-c8b49b#vrvkr=%u5a^wf6@gej1904r0ze(nwnm'
ADMINS = (('Dev', 'juno.kim@bktaxi.com'))
MANAGERS = ADMINS
ROOT_URLCONF = 'cabbie.urls'
WSGI_APPLICATION = 'cabbie.wsgi.application'
LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_L10N = True
USE_TZ = True

BASE_DIR = os.path.realpath(os.path.dirname(__file__))
LOG_DIR = os.path.join(BASE_DIR, 'log')
MEDIA_DIR = os.path.join(BASE_DIR, 'media')
STATIC_DIR = os.path.join(BASE_DIR, 'static')
TEMPLATE_DIRS = (os.path.join(BASE_DIR, 'templates'), )
LOCALE_PATHS = (os.path.join(BASE_DIR, 'locale'), )
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_ROOT = os.path.join(BASE_DIR, 'static/components')
MEDIA_URL = '/media/'
STATIC_URL = '/components/'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'cabbie.common.context_processors.default',
)

MIDDLEWARE_CLASSES = (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'cabbie.common.middleware.DelayMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.gis',

    # 3rd-party apps
    'coffin',
    'djcelery',
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
    'storages',
    'django_ses',
    'django_extensions',
    'debug_toolbar',

    # Admin
    'suit',
    'tinymce',
    'django_wysiwyg',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'import_export',
    'daterange_filter',

    # Project apps
    'cabbie.apps.education',
    'cabbie.apps.affiliation',
    'cabbie.apps.account',
    'cabbie.apps.drive',
    'cabbie.apps.payment',
    'cabbie.apps.recommend',
    'cabbie.apps.stats',
    'cabbie.apps.kpi',
    'cabbie.apps.appversion',
    'cabbie.apps.notice', 
    'cabbie.apps.notification',
    'cabbie.apps.policy',
    'cabbie.apps.event',

    #'cabbie.apps.track',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'cabbie',
        'USER': 'cabbie',
        'PASSWORD': 'roqkfwk1',
        'HOST': 'bktaxi-app-production.cgti7agq49bc.ap-northeast-1.rds.amazonaws.com',
        'PORT': 5432,
    },
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache_table',
        'OPTIONS': {
            'MAX_ENTRIES': 100000
        }
    }

}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'verbose': {
            '()': 'cabbie.utils.log.ColorFormatter',
            'format': '%(asctime)s %(levelname)-8s %(name)-30s %(message)s'
        },
        'simple': {
            '()': 'cabbie.utils.log.ColorFormatter',
            'format': '%(asctime)s %(levelname)-8s %(message)s'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'cabbie.log'),
            'formatter': 'simple'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'cabbie': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}

AUTH_USER_MODEL = 'account.User'
LOGIN_URL = '/login'
LOGOUT_URL = '/logout'
LOGIN_REDIRECT_URL = '/'

APPEND_SLASH = False


# Project settings
# ================

# Basic
# -----

VERSION = 1
HOST = 'bktaxi.com'
ALLOWED_HOSTS = ['*']

# Web
# ---
APP_HOST = 'location-new.{0}'.format(HOST)
API_HOST = 'api-new.{0}'.format(HOST)

WEB_SERVER_HOST = API_HOST
WEB_SERVER_PORT = 443 

LOCATION_SERVER_HOST = APP_HOST
LOCATION_SERVER_PORT = 8080

LOCATION_WEB_SERVER_PORT = 7777



# Email
# -----

CONTACT_EMAIL = '백기사 <support@{host}>'.format(host=HOST)
ALLOWED_DEBUG_EMAIL = ['kokookko1@gmail.com', 'kokookko1@naver.com', 'yousang.lee@bktaxi.com']
EMAIL_DELIMITER = '=====CABBIE====='
EMAIL_BACKEND = 'django_ses.SESBackend'
EMAIL_HOST = 'email-smtp.us-east-1.amazonaws.com'
EMAIL_HOST_USER = 'AKIAJD3WYLRGE5C2HKVA'
EMAIL_HOST_PASSWORD = 'Ala4bqSfpgYFFHi966Ys4eUINKH058fZ85nZYqLKC3yt'
EMAIL_DEFAULT_FONT = 'Arial, Helvetica, sans-serif'     # http://www.w3schools.com/cssref/css_websafe_fonts.asp

# Cloudfront
WEB_CDN_DOMAIN_NAME = 'http://d3qhjk1lhj60db.cloudfront.net'
EMAIL_CDN_DOMAIN_NAME = 'http://d2vgtxzoj7hyhq.cloudfront.net'

# Point
POINT_APPLICATION_URL = 'http://goo.gl/forms/zfzfspdrLY'

# Bktaxi urls
BKTAXI_WEB_URL = 'https://bktaxi.com'
BKTAXI_FACEBOOK_URL = 'https://www.facebook.com/baekkisa'
BKTAXI_INSTAGRAM_URL = 'https://instagram.com/baekkisa'
BKTAXI_NAVER_BLOG_URL = 'http://blog.naver.com/bktaxi0624'


# Jinja2
# ------

# TODO: Automatically import filters & extensions
JINJA2_FILTERS = (
    'cabbie.common.jinja_filters.number',
    'cabbie.common.jinja_filters.duration',
    'cabbie.common.jinja_filters.price',
    'cabbie.common.jinja_filters.percent',
    'cabbie.common.jinja_filters.json',

    'cabbie.common.jinja_filters.startswith',
    'cabbie.common.jinja_filters.endswith',
    'cabbie.common.jinja_filters.strip_tags',
    'cabbie.common.jinja_filters.boolean',

    'cabbie.common.jinja_filters.absolutify',
    'cabbie.common.jinja_filters.add_url_param',
)
JINJA2_EXTENSIONS = (
    'jinja2.ext.autoescape',
    'jinja2.ext.i18n',
    'jinja2.ext.with_',
)
DATE_FORMAT = 'M d, Y'  # For the Jinja2's date filter


# Celery
# ------

BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_TASK_RESULT_EXPIRES = 1 * 60 * 60
CELERY_IMPORTS = (
    'cabbie.utils.email',
    'cabbie.utils.push',
)
CELERYBEAT_SCHEDULE = {
    'update_request_regions': {
        'task': 'cabbie.apps.drive.tasks.UpdateRequestRegionsTask'
        'schedule': crontab(minute='*/5'),   # execute every 5 minutes
    },

    # deprecated
#   'dormant_driver': {
#       'task': 'cabbie.apps.account.tasks.DormantDriverDailyTask',
#       'schedule': crontab(minute=1, hour=0),
#   },
#   'super_driver': {
#       'task': 'cabbie.apps.account.tasks.SuperDriverMonthlyTask',
#       'schedule': crontab(minute=5, hour=0, day_of_month=1),
#   },
#   'compute_hotspot': {
#       'task': 'cabbie.apps.drive.tasks.ComputeHotspotDailyTask',
#       'schedule': crontab(minute=2, hour=0),
#   },
#   'coupon': {
#       'task': 'cabbie.apps.stats.tasks.CouponMonthlyTask',
#       'schedule': crontab(minute=45, hour=0, day_of_month=1),
#   },
}


# REST
# ----

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.DjangoFilterBackend',
        'rest_framework.filters.OrderingFilter',
    ),
    'PAGINATE_BY': 20,
    'PAGINATE_BY_PARAM': 'size',
}


# CORS
# ----

CORS_ORIGIN_ALLOW_ALL = True

# Django debug toolbar
# --------------------
DEBUG_TOOLBAR_PATCH_SETTINGS = False
INTERNAL_IPS = '127.0.0.1'

# Location
# --------

TMAP_API_KEY = '063220b6-6f0b-3741-8349-5bf54cc5f00c'
#TMAP_API_KEY = '1a4dce89-3e7e-3b42-9955-7f1de35a13a5'

DEFAULT_SPEED = 25.0                    # km/h
TMAP_ESTIMATOR_CACHE_TIMEOUT = 10 * 60  # seconds
ESTIMATE_CACHE_TIMEOUT = 5              # seconds
LOCATION_REFRESH_INTERVAL = 3           # seconds
RIDE_ESTIMATE_REFRESH_INTERVAL = 10     # seconds
OBJECT_CACHE_TIMEOUT = 10 * 60          # seconds
SESSION_CLOSE_TIMEOUT = 5               # seconds
MAX_DISTANCE = 5 * 1000                 # meters

# dispatch request
TARGET_DISTANCES = [300, 600, 1000, 1500, 2200]
TERMINATION_DELAY_WITH_NO_CONTACT   = 5     # seconds
TERMINATION_DELAY_WITH_CONTACTS     = 30    # seconds

RIDE_COMPLETE_DISTANCE = 1000           # meters
ESTIMATE_CACHE_DISTANCE = 20            # meters
CANDIDATE_COUNT = 200
REASSIGN_COUNT = 50

REQUEST_TIMEOUT = 20                    # seconds

# Bot
# ---

BOT_LONGITUDE_RANGE = [126.8670047, 127.2054218]
BOT_LATITUDE_RANGE = [37.4706599, 37.605471]


# TMap
# ----

TMAP_CACHE_TIMEOUT = 60 * 60            # seconds


# Suit
# ----

SUIT_CONFIG = {
    'ADMIN_NAME': u'백기사 어드민',
    'MENU_EXCLUDE': ('auth', 'authtoken', 'djcelery',),
    'LIST_PER_PAGE': 100,
}

# Admin wysiwyg
DJANGO_WYSIWYG_FLAVOR = 'tinymce_advanced'


# Storage
# -------

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', 'AKIAIMHVSY5T3QSORJSA')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', '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')
AWS_STORAGE_BUCKET_NAME = 'com.bktaxi'
AWS_LOCATION = 'ap-northeast-1'
#from boto.s3.connection import OrdinaryCallingFormat, SubdomainCallingFormat
#AWS_S3_CALLING_FORMAT = SubdomainCallingFormat() 
#AWS_HEADERS = {} # TODO: Specify the S3 headers (e.g. Cache)

# Parse
# -----
PARSE_API_URL = 'api.parse.com'
PARSE_HTTPS_PORT = 443

PARSE_APPLICATION_ID = '7Zb99LTr2u08bqWjmXAYVqhqEJlXsaGB20oHK7DZ'
PARSE_REST_API_KEY = 'sUDJrgh7zik3ceToqDqD4MReOGsbBbW0uQ11jsdc'
PARSE_MASTER_KEY = 'l1s6VL3IuvsrxZKwM7EAbnxXzvRfAFiLfKcuZtX6'
from parse_rest.connection import register
register(PARSE_APPLICATION_ID, PARSE_REST_API_KEY, master_key=PARSE_MASTER_KEY)

# Objects
PARSE_OBJECT_DRIVER_LOCATION = 'DriverLocation'



PUSH_CHANNEL_PREFIX = None


MESSAGE_RIDE_REQUEST_TITLE = u'콜요청!'
MESSAGE_RIDE_REQUEST_ALERT = u'콜이 요청되었습니다. (30초 이내 수락/거절)'

MESSAGE_RIDE_EXPIRED_TITLE = u'콜이 이미 수락됨'
MESSAGE_RIDE_EXPIRED_ALERT = u'콜이 다른 기사님에 의해 수락되었습니다.'

MESSAGE_RIDE_APPROVE_TITLE = u'콜수락'
MESSAGE_RIDE_APPROVE_ALERT = u'콜이 수락되었습니다.'

MESSAGE_RIDE_PROGRESS_TITLE = u'백기사 접근중'
MESSAGE_RIDE_PROGRESS_ALERT = u'기사님이 픽업장소로 이동중입니다.'

MESSAGE_RIDE_REJECT_TITLE = u'콜거절'
MESSAGE_RIDE_REJECT_ALERT = u'콜이 거절되었습니다.'

MESSAGE_RIDE_CANCEL_TITLE = u'콜취소'
MESSAGE_RIDE_CANCEL_ALERT = u'승객이 콜을 취소하였습니다.'

MESSAGE_RIDE_ARRIVE_TITLE = u'백기사 도착'
MESSAGE_RIDE_ARRIVE_ALERT = u'백기사가 픽업장소에 도착하였습니다.'

MESSAGE_RIDE_COMPLETE_TITLE = u'서비스 평가'
MESSAGE_RIDE_COMPLETE_ALERT = u'백기사 어떠셨나요? 지금 바로 평가해 주세요. (10초소요)'

MESSAGE_RIDE_BOARD_TITLE = u'탑승완료'
MESSAGE_RIDE_BOARD_ALERT = u'백기사를 이용해 주셔서 감사합니다. 편안한 시간되세요!'

# SMS
# ---

ALLOWED_DEBUG_PHONE = ['01026254319', '01038919027']

DRIVER_ACCOUNT_MANAGER = [
    '01045676685',  # Jangwoo Park 
    '01089861391',  # Yuchan Hwang
    '01025069502',  # Hyungsoo Han 
    '01093400443',  # Joonyoung Yoon
    '01091857090',  # Yusang Lee
    '01038919027',  # Juno Kim
    '01099532036'   # Sunghwan Choi
]

RIDE_QA_MANAGERS = [
    '01099532036',  # Sunghwan Choi
    '01038919027',  # Juno Kim
]

SMS_API_KEY = 'MTc1Ni0xNDA4MzYwNDM0MzI0LWMxMjM5YmU3LWNiOWUtNDZkZC1hMzliLWU3Y2I5ZTQ2ZGRkZg=='
SMS_FROM = '18991391'

# Etc
# ---

CRYPTO_KEY = 'xortldhkgkaRpwmf'
DEFAULT_PAGE_SIZE = 20
MASTER_VERIFICATION_CODE = '0624'

BKTAXI_GRAND_LAUNCH_DATE = '2015-03-30'

# Non peak hour
PASSENGER_NON_PEAK_HOUR = [10, 11, 12, 13, 14, 15, 16, 17]

# For driver
DRIVER_REBATE_HOUR = [23, 0, 1]
DRIVER_REBATE_WEEKDAY = [5, 6]      # Fri, Sat
DRIVER_REBATE_UNTIL = '201506'

# Event
# -----

# Signup point
BKTAXI_PASSENGER_SIGNUP_POINT_DUE_DATE = '2015-05-31'

# Recommend event sms
BKTAXI_PASSENGER_RECOMMEND_EVENT_SMS_SEND_ENDS_AT = '2015-06-17'

# Passenger promotion : 5000P (deprecated)
BKTAXI_PASSENGER_RIDE_POINT_PROMOTION_5000P_BEGIN = '2015-07-15'
BKTAXI_PASSENGER_RIDE_POINT_PROMOTION_5000P_END = '2015-07-22'

# Ride point
BKTAXI_PASSENGER_RIDE_POINT_ADJUSTED_FROM = '2015-09-21'
BKTAXI_PASSENGER_RIDE_POINT_ADJUSTED_AMOUNT = 300

POINTS_BY_TYPE = {
    'recommend_p2p': 1000,
    'recommend_p2d': 1000,
    'recommend_d2p': 1000,
    'recommend_d2d': 5000,
    'recommended_d2p': 1000,
    'recommended_p2p': 1000,
    'recommended_p2d': 0,
    'recommended_d2d': 1000,
    'signup_point': 10000,                      # For passenger
    'ride_point': 1000,                         # For passenger
    'ride_point_for_the_affiliated': 2000,      # For affiliated company 
    'rate_point': 0,                            # For passenger
    'rebate': 2000                              # For driver
}
COUPON_THRESHOLDS = (
    (100, 100000),    # (board_count, amount)
    (50, 50000),
    (10, 10000),
)

CALL_FEE = 0

DORMANT_DRIVER_DAYS = 14
SUPER_DRIVER_THRESHOLD = 10

HOTSPOT_COUNT = 100

# Tinymce
TINYMCE_DEFAULT_CONFIG = {
    'theme': 'advanced', 
    'width': 800,
    'height': 800,
}

# Local settings
# --------------

try:
    from local_settings import *
except ImportError:
    pass


# Initialization
# --------------

djcelery.setup_loader()
