# -*- coding: utf-8 -*-
from __future__ import absolute_import

from .project import *  # NOQA

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['hot.geoweb.io']

# Comment if you are not running behind proxy
USE_X_FORWARDED_HOST = True

# Set debug to false for production
DEBUG = False


DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'hot_exports_dev',
        'OPTIONS': {
            'options': '-c search_path=exports,public',
            'sslmode': 'require',
        },
        'CONN_MAX_AGE': None,
        'USER': 'hot',
    }
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['oet2/api/templates/', 'oet2/ui/templates', 'oet2/ui/static/ui/js'],
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
            'debug': DEBUG
        },
    },
]


# session settings
SESSION_COOKIE_NAME = 'hot_exports_sessionid'
SESSION_COOKIE_DOMAIN = 'hot.geoweb.io'
SESSION_COOKIE_PATH = '/'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True


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
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
            'formatter': 'verbose'
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'level': 'DEBUG',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'propagate': True,
            'level': 'ERROR',
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
