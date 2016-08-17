"""Provides validation for API operatios."""

# -*- coding: utf-8 -*-
import logging
import math
import os
from collections import OrderedDict
from StringIO import StringIO

import magic
from lxml import etree

from django.conf import settings
from django.contrib.gis.geos import GEOSException, GEOSGeometry, Polygon
from django.utils.translation import ugettext as _

from rest_framework import serializers

# Get an instance of a logger
logger = logging.getLogger(__name__)


def validate_conifg(uid):
    pass


def validate_region(regions):
    """
    Return the first region found.

    Args:
        regions: a list of Regions.

    Raises:
        ValidationError: if no regions are found.
    """
    if len(regions) == 0:
        detail = OrderedDict()
        detail['id'] = _('invalid_region')
        detail['message'] = _('Job extent is not within a valid region.')
        raise serializers.ValidationError(detail)
    return regions[0]


def validate_formats(data):
    """
    Validate the selected export formats.

    Args:
        data: the submitted form data.

    Raises:
        ValidationError: if there are no formats selected.
    """
    formats = data['formats']
    if formats == None or len(formats) == 0:
        raise serializers.ValidationError({'formats': [_('Select an export format.')]})


def validate_search_bbox(extents):
    """
    Validates the export extents.

    Args:
        extents: a tuple of export extents (xmin, ymin, xmax, ymax)

    Returns:
        a a valid GEOSGeometry.

    Raises:
        ValidationError:    if its not possible
            to create a GEOSGeometry from the provided extents or
            if the resulting GEOSGeometry is invalid.
    """
    detail = OrderedDict()
    detail['id'] = _('invalid_bounds')
    detail['message'] = _('Invalid bounding box.')
    try:
        bbox = Polygon.from_bbox(extents)
        if (bbox.valid):
            return bbox
        else:
            raise serializers.ValidationError(detail)
    except GEOSException as e:
        raise serializers.ValidationError(detail)


def validate_bbox(extents, user=None):
    """
    Validates the extents by calculating the geodesic area of the extents,
    then checking the resulting area against the max_extent for the user.

    Args:
        extents: a tuple containing xmin,ymin,xmax,ymax export extents.
        user: the authenticated user.

    Returns:
        a valid GEOSGeometry.

    Raises:
        ValidationError: if the extents are greater than the allowed max_extent
            for the user, or if the GEOSGeometry cannot be created or
            are invalid.
    """
    max_extent = settings.JOB_MAX_EXTENT
    for group in user.groups.all():
        if hasattr(group, 'export_profile'):
            max_extent = group.export_profile.max_extent
    detail = OrderedDict()
    detail['id'] = _('invalid_bounds')
    detail['message'] = _('Invalid bounding box.')
    try:
        bbox = GEOSGeometry(Polygon.from_bbox(extents), srid=4326)
        if (bbox.valid):
            area = get_geodesic_area(bbox) / 1000000
            if area > max_extent:
                detail['id'] = _('invalid_extents')
                detail['message'] = _('Job extents too large: %(area)s') % {'area': area}
                raise serializers.ValidationError(detail)
            return bbox
        else:
            raise serializers.ValidationError(detail)
    except GEOSException as e:
        raise serializers.ValidationError(detail)


def validate_bbox_params(data):
    """
    Validates the bounding box parameters supplied during form sumission.

    Args:
        the data supplied during form submission.

    Returns:
        a tuple containing the validated extents in the form (xmin,ymin,xmax,ymax).

    Raises:
        ValidationError: if the extents are invalid.
    """
    detail = OrderedDict()

    # test for number
    lon_coords = [float(data['xmin']), float(data['xmax'])]
    lat_coords = [float(data['ymin']), float(data['ymax'])]
    # test lat long value order
    if ((lon_coords[0] >= 0 and lon_coords[0] > lon_coords[1]) or
            (lon_coords[0] < 0 and lon_coords[0] > lon_coords[1])):
        detail['id'] = _('inverted_coordinates')
        detail['message'] = _('xmin greater than xmax.')
        raise serializers.ValidationError(detail)

    if ((lat_coords[0] >= 0 and lat_coords[0] > lat_coords[1]) or
            (lat_coords[0] < 0 and lat_coords[0] > lat_coords[1])):
        detail['id'] = _('inverted_coordinates')
        detail['message'] = _('ymin greater than ymax.')
        raise serializers.ValidationError(detail)

    # test lat long extents
    for lon in lon_coords:
        if (lon < -180 or lon > 180):
            detail['id'] = _('invalid_longitude')
            detail['message'] = _('Invalid longitude coordinate: %(lon)s') % {'lon': lon}
            raise serializers.ValidationError(detail)
    for lat in lat_coords:
        if (lat < -90 and lat > 90):
            detail['id'] = _('invalid_latitude')
            detail['message'] = _('Invalid latitude coordinate: %(lat)s') % {'lat': lat}
            raise serializers.ValidationError(detail)

    return (data['xmin'], data['ymin'], data['xmax'], data['ymax'])


def validate_string_field(name=None, data=None):
    """
    Validates a string.

    Args:
        name (string): the name of the form parameter.
        data (dict): the dict of data submitted during form submission.

    Returns:
        the validated value from the data dict.

    Raises:
        ValidationError: if the value is blank or missing.
    """
    detail = OrderedDict()
    detail['id'] = _('missing_parameter')
    detail['message'] = _('Missing parameter: %(name)s') % {'name': name}
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
    """
    Validates the uploaded configuration file against its declared configuration type.

    Args:
        upload: the uploaded file.
        config_type: the configuration type of the uploaded file.

    Returns:
        the content_type of the validated uploaded file.

    Raises:
        ValidationError: if the uploaded file has invalid content for the provided config_type.
    """
    ACCEPT_MIME_TYPES = {'PRESET': ('application/xml',),
                        'TRANSFORM': ('application/x-sql', 'text/plain'),
                        'TRANSLATION': ('text/plain',)}
    content_type = magic.from_buffer(upload.read(1024), mime=True)
    if (content_type not in ACCEPT_MIME_TYPES[config_type]):
        detail = OrderedDict()
        detail['id'] = _('invalid_content')
        detail['message'] = _('Uploaded config file has invalid content: %(content_type)s') % {'content_type': content_type}
        raise serializers.ValidationError(detail)
    return content_type


def validate_preset(upload):
    """
    Validates a JOSM preset against tagging-preset.xsd.

    Args:
        upload: the uploaded preset.

    Raises:
        ValidationError: if the preset is invalid.
    """
    path = os.path.dirname(os.path.realpath(__file__))
    schema = StringIO(open(path + '/presets/tagging-preset.xsd').read())
    xmlschema_doc = etree.parse(schema)
    xmlschema = etree.XMLSchema(xmlschema_doc)
    upload.open()
    xml = StringIO(upload.read())
    try:
        tree = etree.parse(xml)
    except Exception as e:
        logger.debug(e)
        detail = OrderedDict()
        detail['id'] = _('invalid_content')
        detail['message'] = _('The uploaded preset file is invalid. %(error)s') % {'error': str(e)}
        raise serializers.ValidationError(detail)
    """Validate the uploaded preset."""
    valid = xmlschema.validate(tree)
    if not valid:
        detail = OrderedDict()
        detail['id'] = _('invalid_content')
        detail['message'] = _('The uploaded preset file is an invalid JOSM preset.')
        raise serializers.ValidationError(detail)


def get_geodesic_area(geom):
    """
    Returns the geodesic area of the provided geometry.

    Uses the algorithm to calculate geodesic area of a polygon from OpenLayers 2.
    See http://bit.ly/1Mite1X.

    Args:
        geom (GEOSGeometry): the export extent as a GEOSGeometry.

    Returns
        area (float): the geodesic area of the provided geometry.
    """
    area = 0.0
    coords = geom.coords[0]
    length = len(coords)
    if length > 2:
        for x in range(length - 1):
            p1 = coords[x]
            p2 = coords[x+1]
            area += math.radians(p2[0] - p1[0]) * (2 + math.sin(math.radians(p1[1]))
                                                   + math.sin(math.radians(p2[1])))
        area = area * 6378137 * 6378137 / 2.0
    return area
