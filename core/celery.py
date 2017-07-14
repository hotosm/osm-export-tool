from __future__ import absolute_import

import os

from celery import Celery

# provide a default so that appropriate settings can be loaded
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.project')

from django.conf import settings
from celery.signals import worker_process_init

app = Celery('exports')

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

