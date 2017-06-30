# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os

from celery.schedules import crontab

from .contrib import *  # NOQA

# Celery config
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_DISABLE_RATE_LIMITS = True
CELERY_TASK_SERIALIZER = "json"
CELERY_TRACK_STARTED = True

# configure periodic task
CELERYBEAT_SCHEDULE = {
    'periodic-runs': {
        'task': 'Queue Periodic Runs',
        'schedule': crontab(minute='*/15'),
    },
    'remove-old-downloads': {
        'task': 'Remove Old Downloads',
        'schedule': crontab(hour='*'),
    }
}

BROKER_URL = os.getenv('BROKER_URL', 'amqp://guest:guest@localhost:5672/')
