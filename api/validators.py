# -*- coding: utf-8 -*-
import logging
from collections import OrderedDict

import magic

from django.conf import settings
from django.contrib.gis.geos import GEOSException, GEOSGeometry, Polygon

from rest_framework import serializers

# Get an instance of a logger
logger = logging.getLogger(__name__)

def validate_conifg(uid):
    pass

def validate_region(regions):
    if len(regions) == 0:
        detail = OrderedDict()
        detail['id'] = 'invalid_region'
        detail['message'] = 'Job extent is not within a valid region.'
        raise serializers.ValidationError(detail)
    # region with largest area of intersection returned.
    return regions[0]

def validate_formats(data):
    formats = data['formats']
    if formats == None or len(formats) == 0:
        raise serializers.ValidationError({'formats': ['Select an export format.']})

def validate_search_bbox(extents):
    detail = OrderedDict()
    detail['id'] = 'invalid_bounds'
    detail['message'] = 'Invalid bounding box.'
    try:
        bbox = Polygon.from_bbox(extents)
        if (bbox.valid):
            return bbox
        else:
            raise serializers.ValidationError(detail)
    except GEOSException as e:
        raise serializers.ValidationError(detail)

def validate_bbox(extents, user=None):
    max_extent = settings.JOB_MAX_EXTENT
    for group in user.groups.all():
        if hasattr(group, 'export_profile'):
            max_extent = group.export_profile.max_extent
    detail = OrderedDict()
    detail['id'] = 'invalid_bounds'
    detail['message'] = 'Invalid bounding box.'
    try:
        bbox = GEOSGeometry(Polygon.from_bbox(extents), srid=4326)
        bbox_merc = bbox.transform(3857, clone=True)
        if (bbox.valid and bbox_merc.valid):
            area = bbox_merc.area / 1000000
            if area > max_extent:
                detail['id'] = 'invalid_extents'
                detail['message'] = 'Job extents too large: {0}'.format(area)
                raise serializers.ValidationError(detail)
            return bbox
        else:
            raise serializers.ValidationError(detail)
    except GEOSException as e:
        raise serializers.ValidationError(detail)

def validate_bbox_params(data):
    detail = OrderedDict()

    # test for number
    lon_coords = [float(data['xmin']), float(data['xmax'])]
    lat_coords = [float(data['ymin']), float(data['ymax'])]
    # test lat long value order
    if ((lon_coords[0] >= 0 and lon_coords[0] > lon_coords[1])
        or (lon_coords[0] < 0 and lon_coords[0] > lon_coords[1])):
        detail['id'] = 'inverted_coordinates'
        detail['message'] = 'xmin greater than xmax.'
        raise serializers.ValidationError(detail)

    if ((lat_coords[0] >= 0 and lat_coords[0] > lat_coords[1])
        or (lat_coords[0] < 0 and lat_coords[0] > lat_coords[1])):
        detail['id'] = 'inverted_coordinates'
        detail['message'] = 'ymin greater than ymax.'
        raise serializers.ValidationError(detail)

    # test lat long extents
    for lon in lon_coords:
        if (lon < -180 or lon > 180):
            detail['id'] = 'invalid_longitude'
            detail['message'] = 'Invalid longitude coordinate: {0}'.format(lon)
            raise serializers.ValidationError(detail)
    for lat in lat_coords:
        if (lat < -90 and lat > 90):
            detail['id'] = 'invalid_latitude'
            detail['message'] = 'Invalid latitude coordinate: {0}'.format(lat)
            raise serializers.ValidationError(detail)

    return (data['xmin'], data['ymin'], data['xmax'], data['ymax'])

def validate_string_field(name=None, data=None):
    detail = OrderedDict()
    detail['id'] = 'missing_parameter'
    detail['message'] = 'Missing parameter: {0}'.format(name)
    detail['param'] = name
    try:
        value = data[name]
        if value == None or value == '':
            raise serializers.ValidationError(detail)
        else:
            return value
    except Exception:
        raise serializers.ValidationError(detail)

def validate_content_type(upload, config_type):
    ACCEPT_MIME_TYPES = {'PRESET': ('application/xml',),
                        'TRANSFORM': ('application/x-sql', 'text/plain'),
                        'TRANSLATION': ('text/plain',)}
    content_type = magic.from_buffer(upload.read(1024), mime=True)
    if (content_type not in ACCEPT_MIME_TYPES[config_type]):
        detail = OrderedDict()
        detail['id'] = 'invalid_content'
        detail['message'] = 'Uploaded config file has invalid content: {0}'.format(content_type)
        raise serializers.ValidationError(detail)
    return content_type
