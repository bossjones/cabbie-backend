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
ADMINS = (('Dev', 'mjipeo@gmail.com'),('Dev', 'juno.kim@bktaxi.com'))
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
    'cabbie.common.middleware.DelayMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
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

    # Admin
    'suit',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'import_export',
    'daterange_filter',

    # Project apps
    'cabbie.apps.account',
    'cabbie.apps.drive',
    'cabbie.apps.payment',
    'cabbie.apps.recommend',
    'cabbie.apps.stats',
    'cabbie.apps.appversion',
    'cabbie.apps.notification',

    #'cabbie.apps.track',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'cabbie',
        'USER': 'cabbie',
        'PASSWORD': 'roqkfwk1',
        'HOST': 'cabbie.cgti7agq49bc.ap-northeast-1.rds.amazonaws.com',
        'PORT': 5432,
    },
}

CACHES = {
    'default': {
        'BACKEND': 'redis_cache.cache.RedisCache',
        'LOCATION': '127.0.0.1:6379:1',
        'OPTIONS': {
            'CLIENT_CLASS': 'redis_cache.client.DefaultClient',
        },
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
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'cabbie': {
            'handlers': ['file'],
            'level': 'INFO',
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
ALLOWED_HOSTS = ['.{0}'.format(HOST)]


# Email
# -----

CONTACT_EMAIL = 'Cabbie <contact@{host}>'.format(host=HOST)
ALLOWED_DEBUG_EMAIL = ['mjipeo@gmail.com']
EMAIL_DELIMITER = '=====CABBIE====='
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'email-smtp.us-east-1.amazonaws.com'
EMAIL_HOST_USER = 'AKIAJD3WYLRGE5C2HKVA'
EMAIL_HOST_PASSWORD = 'Ala4bqSfpgYFFHi966Ys4eUINKH058fZ85nZYqLKC3yt'



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
    'dormant_driver': {
        'task': 'cabbie.apps.account.tasks.DormantDriverDailyTask',
        'schedule': crontab(minute=1, hour=0),
    },
    'super_driver': {
        'task': 'cabbie.apps.account.tasks.SuperDriverMonthlyTask',
        'schedule': crontab(minute=5, hour=0, day_of_month=1),
    },
    'compute_hotspot': {
        'task': 'cabbie.apps.drive.tasks.ComputeHotspotDailyTask',
        'schedule': crontab(minute=2, hour=0),
    },
    'coupon': {
        'task': 'cabbie.apps.stats.tasks.CouponMonthlyTask',
        'schedule': crontab(minute=45, hour=0, day_of_month=1),
    },
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


# Location
# --------

LOCATION_SERVER_HOST = 'bktaxi.com'
LOCATION_SERVER_PORT = 8080
#TMAP_API_KEY = '063220b6-6f0b-3741-8349-5bf54cc5f00c'
TMAP_API_KEY = '1a4dce89-3e7e-3b42-9955-7f1de35a13a5'

DEFAULT_SPEED = 40.0                    # km/h
TMAP_ESTIMATOR_CACHE_TIMEOUT = 10 * 60  # seconds
ESTIMATE_CACHE_TIMEOUT = 1 * 60         # seconds
LOCATION_REFRESH_INTERVAL = 1           # seconds
RIDE_ESTIMATE_REFRESH_INTERVAL = 10     # seconds
OBJECT_CACHE_TIMEOUT = 10 * 60          # seconds
SESSION_CLOSE_TIMEOUT = 3               # seconds
MAX_DISTANCE = 10 * 1000                # meters
ESTIMATE_CACHE_DISTANCE = 200           # meters
CANDIDATE_COUNT = 10
REASSIGN_COUNT = 10


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


# Storage
# -------

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', 'AKIAIMHVSY5T3QSORJSA')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', 'cRTKdqakXbhUTsHrzbi/97mOADRboHH/v5/q0jbS')
AWS_STORAGE_BUCKET_NAME = 'com.bktaxi'
#AWS_HEADERS = {} # TODO: Specify the S3 headers (e.g. Cache)

# Push (Parse)
PARSE_APPLICATION_ID = '7Zb99LTr2u08bqWjmXAYVqhqEJlXsaGB20oHK7DZ'
PARSE_REST_API_KEY = 'sUDJrgh7zik3ceToqDqD4MReOGsbBbW0uQ11jsdc'
PARSE_MASTER_KEY = 'l1s6VL3IuvsrxZKwM7EAbnxXzvRfAFiLfKcuZtX6'
from parse_rest.connection import register
register(PARSE_APPLICATION_ID, PARSE_REST_API_KEY, master_key=PARSE_MASTER_KEY)

MESSAGE_RIDE_COMPLETE_TITLE = u'목적지 도착!'
MESSAGE_RIDE_COMPLETE_ALERT = u'백기사 어떠셨나요? 지금 바로 평가해 주세요. (10초소요)'

# SMS
# ---

ALLOWED_DEBUG_PHONE = ['01026254319', '01038919027']
SMS_API_KEY = 'MTc1Ni0xNDA4MzYwNDM0MzI0LWMxMjM5YmU3LWNiOWUtNDZkZC1hMzliLWU3Y2I5ZTQ2ZGRkZg=='
SMS_FROM = '027202036'

# Etc
# ---

CRYPTO_KEY = 'xortldhkgkaRpwmf'
DEFAULT_PAGE_SIZE = 20

DRIVER_REBATE_UNTIL = '201506'

NON_PEAK_DAYS = [0, 1, 2, 3]   # Mon, Tue, Wed, Thu

PEAK_HOUR = [11, 0, 1]

POINTS_BY_TYPE = {
    'recommend_p2p': 1000,
    'recommend_p2d': 1000,
    'recommend_d2p': 1000,
    'recommend_d2d': 5000,
    'recommended_d2p': 1000,
    'recommended_p2p': 1000,
    'recommended_p2d': 0,
    'recommended_d2d': 1000,
    'mileage': 100,                 # For passenger
    'mileage_non_peak_day': 500,    # For passenger
    'rebate': 2000                  # For driver
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


# Local settings
# --------------

try:
    from local_settings import *
except ImportError:
    pass


# Initialization
# --------------

djcelery.setup_loader()
