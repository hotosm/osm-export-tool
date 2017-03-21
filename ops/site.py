# -*- coding: utf-8 -*-
from __future__ import absolute_import

import dj_database_url

from .prod import *  # NOQA

ALLOWED_HOSTS = ['172.16.142.145']
SESSION_COOKIE_DOMAIN = '172.16.142.145'
HOSTNAME = '172.16.142.145'
TASK_ERROR_EMAIL = 'seth@mojodna.net'
DEBUG = True
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DATABASES['default'] = dj_database_url.config(default='postgres://exports:exports@localhost:5432/exports')
DATABASES['default']['ENGINE'] = 'django.contrib.gis.db.backends.postgis'


EXPORT_STAGING_ROOT = '/opt/staging/'

# where exports are stored for public download
EXPORT_DOWNLOAD_ROOT = '/opt/download/'

# the root url for export downloads
EXPORT_MEDIA_ROOT = '/downloads/'

# home dir of the OSMAnd Map Creator
OSMAND_MAP_CREATOR_DIR = '/opt/osmandmapcreator'

# location of the garmin config file
# TODO place this
GARMIN_CONFIG = '/opt/osm-export-tool2/utils/conf/garmin_config.xml'

OVERPASS_API_URL = 'http://overpass-api.de/api/interpreter'
