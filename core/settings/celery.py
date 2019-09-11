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

BROKER_URL = os.getenv('BROKER_URL', 'amqp://guest:guest@localhost:5672/')
