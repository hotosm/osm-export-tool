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
def recreate_http_client(signal, sender):
    # make sure each process has a different instance of RemoteCKAN to deal with SSL and session bugs
    Configuration.read().setup_remoteckan()
