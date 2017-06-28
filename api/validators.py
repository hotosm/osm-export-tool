"""Provides validation for API operations."""

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
LOG = logging.getLogger(__name__)

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
        if bbox.valid:
            return bbox
        else:
            raise serializers.ValidationError(detail)
    except GEOSException:
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







