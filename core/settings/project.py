# -*- coding: utf-8 -*-
from __future__ import absolute_import

from .celery import *  # NOQA

# Project apps
INSTALLED_APPS += (
    'jobs',
    'tasks',
    'api',
    'ui',
    'utils',
)

LOGIN_URL = '/login/'

EXPORT_TASKS = {
    'pbf': 'tasks.export_tasks.PbfExportTask',
    'shp': 'tasks.export_tasks.ShpExportTask',
    'obf': 'tasks.export_tasks.ObfExportTask',
    'sqlite': 'tasks.export_tasks.SqliteExportTask',
    'kml': 'tasks.export_tasks.KmlExportTask',
    'garmin': 'tasks.export_tasks.GarminExportTask',
    'thematic': 'tasks.export_tasks.ThematicLayersExportTask'
}

# where exports are staged for processing
EXPORT_STAGING_ROOT = '/home/ubuntu/export_staging/'

# where exports are stored for public download
EXPORT_DOWNLOAD_ROOT = '/home/ubuntu/export_downloads/'

# the root url for export downloads
EXPORT_MEDIA_ROOT = '/downloads/'

# home dir of the OSMAnd Map Creator
OSMAND_MAP_CREATOR_DIR = '/home/ubuntu/osmand/OsmAndMapCreator'

# location of the garmin config file
GARMIN_CONFIG = '/home/ubuntu/www/hotosm/utils/conf/garmin_config.xml'

# url to overpass api endpoint
OVERPASS_API_URL = 'http://localhost/interpreter'

"""
Maximum extent of a Job
max of (latmax-latmin) * (lonmax-lonmin)
"""
JOB_MAX_EXTENT = 2500000  # default export max extent in sq km

# maximum number of runs to hold for each export
EXPORT_MAX_RUNS = 5

HOSTNAME = 'hot.geoweb.io'

"""
Admin email address
which receives task error notifications.
"""
TASK_ERROR_EMAIL = 'export-tool@hotosm.org'

"""
Overpass Element limit

Sets the max ram allowed for overpass query

http://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_QL#Element_limit_.28maxsize.29
"""

OVERPASS_MAX_SIZE = 2147483648  # 2GB

"""
Overpass timeout setting

Sets request timeout for overpass queries.

http://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_QL#timeout
"""

OVERPASS_TIMEOUT = 1600  # query timeout in seconds
