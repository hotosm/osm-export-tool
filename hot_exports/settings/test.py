# -*- coding: utf-8 -*-
from __future__ import absolute_import

from .project import *  # noqa

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'hot_exports_dev',
        'OPTIONS': {
            'options': '-c search_path=exports,public',
            'sslmode': 'require',
        },
        'CONN_MAX_AGE': None,
        'USER': 'dodobas',
        'HOST': 'localhost'
    }
}

INSTALLED_APPS += (
    'django_nose',
)

# Use default Django test runner
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'


EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
# change this to a proper location
EMAIL_FILE_PATH = '/tmp/'


# Do not log anything during testing
LOGGING = {
    # internal dictConfig version - DON'T CHANGE
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'nullhandler': {
            'class': 'logging.NullHandler',
        },
    },
    # default root logger
    'root': {
        'level': 'DEBUG',
        'handlers': ['nullhandler'],
    }
}


"""
NOSE_ARGS = [
    '--with-coverage',
    '--cover-html',
    '--cover-html-dir=cover',
    '--cover-package=api,tasks,jobs,utils'
]
"""
