"""Provides validation for API operations."""

# -*- coding: utf-8 -*-
from collections import OrderedDict

from django.contrib.gis.geos import GEOSException, Polygon
from django.utils.translation import gettext as _

from rest_framework import serializers


def validate_search_bbox(extents):
    """
    Validates the export extents.

    Args:
        extents: a tuple of export extents (xmin, ymin, xmax, ymax)

    Returns:
        a valid GEOSGeometry.

    Raises:
        ValidationError: if a GEOSGeometry cannot be created from the extents
            or the resulting geometry is invalid.
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
