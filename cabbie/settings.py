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
ADMINS = (('Dev', 'mjipeo@gmail.com'),)
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
    'django.contrib.sessions.middleware.SessionMiddleware',
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

    # 3rd-party apps
    'coffin',
    'djcelery',
    'rest_framework',
    'rest_framework.authtoken',

    # Admin
    'django.contrib.admin',
    'django.contrib.admindocs',

    # Project apps
    'cabbie.apps.account',
    'cabbie.apps.drive',
    'cabbie.apps.payment',
    'cabbie.apps.notification',
    'cabbie.apps.stats',
    'cabbie.apps.track',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'cabbie',
        'USER': 'cabbie',
        'PASSWORD': 'zoql123',
        'HOST': '127.0.0.1',
        'PORT': '',
        'OPTIONS': {
            'init_command': 'SET storage_engine=INNODB',
        },
    },
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
            'formatter': 'verbose'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'cabbie.log'),
            'formatter': 'verbose'
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
            'propagate': True,
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
HOST = 'cabbie.com'
ALLOWED_HOSTS = ['.{0}'.format(HOST)]


# Email
# -----

CONTACT_EMAIL = 'Cabbie <contact@{host}>'.format(host=HOST)
ALLOWED_DEBUG_EMAIL = ['mjipeo@gmail.com']
EMAIL_DELIMITER = '=====CABBIE====='


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
CELERYBEAT_SCHEDULE = {}


# REST
# ----

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',),
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',),
    'PAGINATE_BY': 10,
}


# Location
# --------

LOCATION_SERVER_PORT = 8080



# Local settings
# --------------

try:
    from local_settings import *
except ImportError:
    pass


# Initialization
# --------------

djcelery.setup_loader()
