# noqa
# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os

import dj_database_url

from .base import *
from .celery import *  # NOQA
from .utils import ABS_PATH
from hdx.configuration import Configuration

# Project apps
INSTALLED_APPS += (
    'jobs',
    'tasks',
    'api',
    'ui',
    'utils',
)

DATABASES = {}

DATABASES['default'] = dj_database_url.config(default='postgres:///exports')
DATABASES['default']['ENGINE'] = 'django.contrib.gis.db.backends.postgis'

CELERY_IMPORTS = (
    'tasks.scheduled_tasks',
    'tasks.task_runners',
)

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
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.contrib.messages.context_processors.messages',
                'social.apps.django_app.context_processors.backends',
                'social.apps.django_app.context_processors.login_redirect',
            ],
            'debug': DEBUG
        },
    },
]

LOGIN_URL = '/login/'

# where exports are staged for processing
EXPORT_STAGING_ROOT = ABS_PATH('../export_staging/')

# where exports are stored for public download
EXPORT_DOWNLOAD_ROOT = ABS_PATH('../export_downloads/')

# the root url for export downloads
EXPORT_MEDIA_ROOT = '/downloads/'

OSMAND_MAP_CREATOR_DIR = os.getenv('OSMAND_MAP_CREATOR_DIR', '/opt/osmandmapcreator/')
GARMIN_SPLITTER = os.getenv('GARMIN_SPLITTER', '/opt/splitter/splitter.jar')
GARMIN_MKGMAP = os.getenv('GARMIN_MKGMAP', '/opt/mkgmap/mkgmap.jar')

# url to overpass api endpoint
OVERPASS_API_URL = os.getenv('OVERPASS_API_URL', 'http://overpass-api.de/api/')

"""
Maximum extent of a Job
max of (latmax-latmin) * (lonmax-lonmin)
"""
JOB_MAX_EXTENT = 2500000  # default export max extent in sq km

HOSTNAME = os.getenv('HOSTNAME', 'export.hotosm.org')

# Comment if you are not running behind proxy
USE_X_FORWARDED_HOST = bool(os.getenv('USE_X_FORWARDED_HOST'))

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
if not DEBUG:
    ALLOWED_HOSTS = [HOSTNAME]

"""
Overpass Element limit

Sets the max ram allowed for overpass query

http://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_QL#Element_limit_.28maxsize.29
"""

OVERPASS_MAX_SIZE = 2147483648  # 2GB

"""
Overpass timeout setting

Sets request timeout for overpass queries.

http://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_QL#timeout
"""

OVERPASS_TIMEOUT = 1600  # query timeout in seconds

if os.getenv('DJANGO_ENV') == 'development':
    INSTALLED_APPS += (
        'django_extensions',
    )

    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

    LOGGING_OUTPUT_ENABLED = DEBUG
    LOGGING_LOG_SQL = DEBUG

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'level': os.getenv('LOG_LEVEL', 'DEBUG'),
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
            'level': os.getenv('DJANGO_LOG_LEVEL', 'ERROR'),
        },
        'api': {
            'handlers': ['console'],
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
            'handlers': ['console'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'celery.task': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'jobs': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'jobs.tests': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'utils': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'utils.tests': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'hot_exports': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'hdx_exports': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'DEBUG',
        },
    }
}

EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_PORT = os.getenv('EMAIL_PORT')
EMAIL_USE_TLS = bool(os.getenv('EMAIL_USE_TLS'))

SPATIALITE_LIBRARY_PATH = 'mod_spatialite'

SYNC_TO_HDX = bool(os.getenv('SYNC_TO_HDX'))
HDX_API_KEY = os.getenv('HDX_API_KEY')
HDX_NOTIFICATION_EMAIL = os.getenv('HDX_NOTIFICATION_EMAIL')
HDX_SITE = os.getenv('HDX_SITE', 'demo')

GEONAMES_API_URL = os.getenv('GEONAMES_API_URL', 'http://api.geonames.org/searchJSON')

HDX_URL_PREFIX = Configuration.create(
    hdx_site=os.getenv('HDX_SITE', 'demo'),
    hdx_key=os.getenv('HDX_API_KEY'),
)
