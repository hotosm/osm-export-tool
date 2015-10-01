from __future__ import absolute_import

from django.conf import settings

from celery import Celery

# celery is going to be executed on the command line or via system scripts
# it's assumed that DJANGO_SETTINGS_MODULE environment variable is set

app = Celery(
    'exports',
    broker='amqp://',
    backend='amqp://'
)


# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
