# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os

from celery.schedules import crontab

from .contrib import *  # NOQA

# Celery config
CELERY_TRACK_STARTED = True

# Pickle used to be the default, and accepting pickled content is a security concern.  Using the new default json,
# causes a circular reference error, that will need to be resolved.
CELERY_TASK_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]

# configure periodic task
CELERYBEAT_SCHEDULE = {
    'periodic-runs': {
        'task': 'Queue Periodic Runs',
        'schedule': crontab(minute='*/15'),
    }
}

BROKER_URL = os.getenv('BROKER_URL', 'amqp://guest:guest@localhost:5672/')
