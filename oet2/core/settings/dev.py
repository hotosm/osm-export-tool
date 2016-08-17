# -*- coding: utf-8 -*-
from __future__ import absolute_import

from .secret import *

#import django
#django.setup()

from .project import *  # NOQA

# Set debug to True for development
DEBUG = True
LOGGING_OUTPUT_ENABLED = DEBUG
LOGGING_LOG_SQL = DEBUG

INSTALLED_APPS += (
    'django_extensions',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'oet2',
        'OPTIONS': {
            'options': '-c search_path=exports,public',
        },
        'CONN_MAX_AGE': None,
        'USER': 'ortelius',
        'HOST': 'localhost'
    }
}


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
            'debug': DEBUG
        },
    },
]

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable caching while in development
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

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
