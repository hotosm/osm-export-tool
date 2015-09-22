"""
Django settings for hot_exports project.

Generated by 'django-admin startproject' using Django 1.8.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

from __future__ import absolute_import

import os
import sys
from hot_exports import settings_private
from celery.schedules import crontab
from django.utils.translation import ugettext_lazy as _

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'r2&#mffb%gjqo_!+^_a_r09vza_el-^ca0h=%zvu_o%+ptt*^&'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

LOGIN_URL = '/login/'

# OAuth login settings
SOCIAL_AUTH_OPENSTREETMAP_LOGIN_URL = '/osm/login/'
SOCIAL_AUTH_OPENSTREETMAP_KEY = '56e4WINtKE9BSzIU1JtYZufLRBp0La5zS6qHvei3'
SOCIAL_AUTH_OPENSTREETMAP_SECRET = 'fcwFW11HB3zFDUQonYUTS3QJEQ5IAowWmISu2l93'
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/exports/create/'
SOCIAL_AUTH_LOGIN_ERROR_URL = '/osm/error'
SOCIAL_AUTH_URL_NAMESPACE = 'osm'
SOCIAL_AUTH_ADMIN_USER_SEARCH_FIELDS = ['username', 'first_name', 'email']
SOCIAL_AUTH_FORCE_EMAIL_VALIDATION = True
SOCIAL_AUTH_EMAIL_VALIDATION_FUNCTION = 'ui.pipeline.email_validation'
SOCIAL_AUTH_EMAIL_VALIDATION_URL = '/osm/email_verify_sent/'

#SOCIAL_AUTH_STRATEGY = 'social.strategies.django_strategy.DjangoStrategy'
#SOCIAL_AUTH_STORAGE = 'social.apps.django_app.default.models.DjangoStorage'

SOCIAL_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social.pipeline.social_auth.social_user',
    'social.pipeline.user.get_username',
    'ui.pipeline.require_email',
    'social.pipeline.mail.mail_validation',
    'social.pipeline.social_auth.associate_by_email',
    'social.pipeline.user.create_user',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.debug.debug',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.user_details'
)

ALLOWED_HOSTS = ['hot.geoweb.io']


# Application definition

DEFAULT_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'django.contrib.postgres',
    'django.contrib.sites',
)

THIRD_PARTY_APPS = (
    'rest_framework',
    'rest_framework_gis',
    'rest_framework.authtoken',
    'django_nose',
    'django_extensions',
    'social.apps.django_app.default'
)

LOCAL_APPS = (
    'jobs',
    'tasks',
    'api',
    'ui',
    'utils',
)

INSTALLED_APPS = DEFAULT_APPS + THIRD_PARTY_APPS + LOCAL_APPS

AUTHENTICATION_BACKENDS = (
    'social.backends.openstreetmap.OpenStreetMapOAuth',
    'social.backends.email.EmailAuth',
    'social.backends.username.UsernameAuth',
    'django.contrib.auth.backends.ModelBackend',
)


MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'social.apps.django_app.middleware.SocialAuthExceptionMiddleware',
)

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',
                                'rest_framework.filters.SearchFilter',
                                'rest_framework.filters.OrderingFilter'), 
    'DEFAULT_AUTHENTICATION_CLASSES': ('rest_framework.authentication.SessionAuthentication',
                                       'rest_framework.authentication.TokenAuthentication'),
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated',),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'api.renderers.HOTExportApiRenderer',
    ),
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.AcceptHeaderVersioning',
    'DEFAULT_VERSION': '1.0',
}

ROOT_URLCONF = 'hot_exports.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['api/templates/', 'ui/templates', 'ui/static/ui/js'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.core.context_processors.i18n',
                'django.core.context_processors.media',
                'django.contrib.messages.context_processors.messages',
                'social.apps.django_app.context_processors.backends',
                'social.apps.django_app.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'hot_exports.wsgi.application'

# session settings
SESSION_COOKIE_NAME='hot_exports_sessionid'
SESSION_COOKIE_DOMAIN='hot.geoweb.io'
SESSION_COOKIE_PATH='/'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

SITE_ID = 1


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

# see settings_private.py
DATABASES = settings_private.DATABASES

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en'

LANGUAGES = (
    ('en', 'English'),
    ('id', 'Bahasa Indonesia'),
    ('de', 'Deutsch'),
    ('es', 'Spanish'),
    ('ja', 'Japanese'),
    ('fr', 'French'),
)

DEFAULT_CHARSET = 'UTF-8'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locales/'),
)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
            'formatter': 'verbose'
        },
        'console': {
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'formatter': 'simple'
        },
    },
    'loggers': {
        'django': {
            'handlers':['file'],
            'propagate': True,
            'level':'ERROR',
        },
        'api': {
            'handlers': ['file'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'api.tests': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'tasks.tests': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'tasks': {
            'handlers': ['file'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'celery.task': {
            'handlers': ['file'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'jobs': {
            'handlers': ['file'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'jobs.tests': {
            'handlers': ['console', 'file'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'utils': {
            'handlers': ['file'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'utils.tests': {
            'handlers': ['console', 'file'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'hot_exports': {
            'handlers': ['file'],
            'propagate': True,
            'level': 'DEBUG',
        },    
    }
}

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
"""
NOSE_ARGS = [
    '--with-coverage',
    '--cover-html',
    '--cover-html-dir=cover',
    '--cover-package=api,tasks,jobs,utils'
]
"""
# Celery config
CELERY_TRACK_STARTED = True

"""
 IMPORTANT
 
 Don't propagate exceptions in the celery chord header to the finalize task.
 If exceptions are thrown in the chord header then allow the
 finalize task to collect the results and update the overall run state.
 
 @see tasks.task_runners.ExportTaskRunner#161
 
"""
CELERY_CHORD_PROPAGATES = False

# configure periodic task
CELERYBEAT_SCHEDULE = {
    'purge-unpublished-exports': {
        'task': 'Purge Unpublished Exports',
        'schedule': crontab(minute='*',hour='*',day_of_week='*')
    },
}

"""
A mapping of supported export formats to ExportTask handler classes
"""
EXPORT_TASKS = {
    'shp': 'tasks.export_tasks.ShpExportTask',
    'obf': 'tasks.export_tasks.ObfExportTask',
    'sqlite': 'tasks.export_tasks.SqliteExportTask',
    'kml': 'tasks.export_tasks.KmlExportTask',
    'garmin': 'tasks.export_tasks.GarminExportTask',
    'thematic': 'tasks.export_tasks.ThematicLayersExportTask'
}

# where exports are staged for processing
EXPORT_STAGING_ROOT = '/home/ubuntu/export_staging/'

# where exports are stored for public download
EXPORT_DOWNLOAD_ROOT = '/home/ubuntu/export_downloads/'

# the root url for export downloads
EXPORT_MEDIA_ROOT = '/downloads/'

# home dir of the OSMAnd Map Creator
OSMAND_MAP_CREATOR_DIR = '/home/ubuntu/osmand/OsmAndMapCreator'

# location of the garmin config file
GARMIN_CONFIG = '/home/ubuntu/www/hotosm/utils/conf/garmin_config.xml'

# url to overpass api endpoint
OVERPASS_API_URL = 'http://localhost/interpreter'

"""
Maximum extent of a Job
max of (latmax-latmin) * (lonmax-lonmin)
"""
JOB_MAX_EXTENT = 2500000 # default export max extent in sq km

# maximum number of runs to hold for each export
EXPORT_MAX_RUNS = 5

HOSTNAME = 'hot.geoweb.io'
