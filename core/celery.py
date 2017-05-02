from __future__ import absolute_import

import os

from celery import Celery

# provide a default so that appropriate settings can be loaded
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.project')

from django.conf import settings
from celery.signals import worker_process_init

from hdx.configuration import Configuration

app = Celery('exports')

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@worker_process_init.connect
def something(signal, sender):
    Configuration.create(
        hdx_site=os.getenv('HDX_SITE', 'demo'),
        hdx_key=os.getenv('HDX_API_KEY'),
    )
