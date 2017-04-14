# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os

import dj_database_url

from .base import *
from .celery import *  # NOQA
from .utils import ABS_PATH

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

# home dir of the OSMAnd Map Creator
OSMAND_MAP_CREATOR_DIR = ABS_PATH('../osmandmapcreator')

# location of the garmin config file
GARMIN_CONFIG = ABS_PATH('utils/conf/garmin_config.xml')

# url to overpass api endpoint
OVERPASS_API_URL = os.environ.get('OVERPASS_API_URL', 'http://overpass-api.de/api/interpreter')

"""
Maximum extent of a Job
max of (latmax-latmin) * (lonmax-lonmin)
"""
JOB_MAX_EXTENT = 2500000  # default export max extent in sq km

HOSTNAME = os.environ.get('HOSTNAME', 'export.hotosm.org')

# Comment if you are not running behind proxy
USE_X_FORWARDED_HOST = bool(os.environ.get('USE_X_FORWARDED_HOST', False))

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
if not DEBUG:
    ALLOWED_HOSTS = [HOSTNAME]

"""
Admin email address
which receives task error notifications.
"""
TASK_ERROR_EMAIL = os.environ.get('TASK_ERROR_EMAIL', 'export-tool@hotosm.org')

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

if os.environ.get('DJANGO_ENV', None) == 'development':
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
            'level': os.environ.get('LOG_LEVEL', 'DEBUG'),
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
            'level': os.environ.get('DJANGO_LOG_LEVEL', 'ERROR'),
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

EMAIL_HOST = os.environ.get('EMAIL_HOST', None)
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', None)
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', None)
EMAIL_PORT = os.environ.get('EMAIL_PORT', None)
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', None)

SPATIALITE_LIBRARY_PATH = 'mod_spatialite'

SYNC_TO_HDX = bool(os.environ.get('SYNC_TO_HDX', False))

GEONAMES_API_URL = os.getenv('GEONAMES_API_URL', 'http://api.geonames.org/searchJSON')
