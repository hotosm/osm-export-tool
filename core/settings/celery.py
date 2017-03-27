# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os

from celery.schedules import crontab

from .contrib import *  # NOQA

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

# Pickle used to be the default, and accepting pickled content is a security concern.  Using the new default json,
# causes a circular reference error, that will need to be resolved.
CELERY_TASK_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]

# configure periodic task
CELERYBEAT_SCHEDULE = {
    'check-overpass': {
        'task': 'Check Overpass',
        'schedule': crontab(minute='*', hour='*', day_of_week='*')
    }
}

BROKER_URL = os.environ.get('BROKER_URL', 'amqp://guest:guest@localhost:5672/')
