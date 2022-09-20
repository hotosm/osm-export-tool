"""
WSGI config for osm-export-tool2 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

import dramatiq_dashboard

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.project")

application = get_wsgi_application()

dashboard_middleware = dramatiq_dashboard.make_wsgi_middleware("/worker-dashboard")
application = dashboard_middleware(application)
