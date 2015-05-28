import logging
from uuid import UUID
from rest_framework import serializers
from rest_framework.reverse import reverse
from django.utils.datastructures import MultiValueDictKeyError
from hot_exports import settings
from django.contrib.gis.geos import Polygon, GEOSException


# Get an instance of a logger
logger = logging.getLogger(__name__)

def validate_region(regions):
    if len(regions) == 0:
        detail={'id': 'invalid_region', 'message': 'Job extent is not within a valid region.'}
        raise serializers.ValidationError(detail)
    # region with largest area of intersection returned.
    return regions[0]

def validate_formats(request):
    scheme = request.scheme
    host = request.META['HTTP_HOST']
    formats_url = '{0}://{1}{2}'.format(scheme, host, reverse('api:formats-list'))
    missing_id = 'missing_format'
    missing_message = 'Export format uid required.'
    invalid_id = 'invalid_format_uid'
    invalid_message = 'Invalid export format uid.'
    formats = request.data.getlist('formats')
    if len(formats) == 0:
        raise serializers.ValidationError(detail = {'id': missing_id,
                'message': missing_message,
                'formats_url': formats_url
            })
    for format in formats:
        try:
            UUID(format, version=4)
        except ValueError:
            raise serializers.ValidationError(detail = {'id': invalid_id,
                'message': invalid_message,
                'formats_url': formats_url
            })

def validate_search_bbox(extents):
    try:
        bbox = Polygon.from_bbox(extents)
        if (bbox.valid):
            return bbox
        else:
            raise serializers.ValidationError(detail={'id': 'invalid_bounds', 'message': 'Invalid bounding box.'})
    except GEOSException as e:
        raise serializers.ValidationError(detail={'id': 'invalid_bounds', 'message': 'Invalid bounding box.'}) 


def validate_bbox(extents):
    try:
        bbox = Polygon.from_bbox(extents)
        if (bbox.valid):
            logger.debug(bbox.area)
            if bbox.area > settings.JOB_MAX_EXTENT:
                raise serializers.ValidationError(detail={'id': 'invalid_extents', 'message': 'Job extents too large.'})
            return bbox
        else:
            raise serializers.ValidationError(detail={'id': 'invalid_bounds', 'message': 'Invalid bounding box.'})
    except GEOSException as e:
        raise serializers.ValidationError(detail={'id': 'invalid_bounds', 'message': 'Invalid bounding box.'}) 

def validate_bbox_params(data):
    try:
        # test we have all params
        xmin = data['xmin']
        ymin = data['ymin']
        xmax = data['xmax']
        ymax = data['ymax']
        
        # test not empty
        for ex in [xmin, ymin, xmax, ymax]:
            if ex == None or ex == '':
                detail={'id': 'empty_bbox_parameter', 'message': 'Empty bounding box parameter.'}
                raise serializers.ValidationError(detail)
        
        # test for number
        lon_coords = []
        lat_coords = []
        try: 
            lon_coords = [float(xmin), float(xmax)]
            lat_coords = [float(ymin), float(ymax)]
        except ValueError as e:
            val = e.message.split(':')[1]
            detail={'id': 'invalid_coordinate', 'message': 'Invalid coordinate: {0}'.format(val)}
            raise serializers.ValidationError(detail)
        
        # test lat long value order
        if ((lon_coords[0] >= 0 and lon_coords[0] > lon_coords[1])
            or (lon_coords[0] < 0 and lon_coords[0] > lon_coords[1])):
            raise serializers.ValidationError(detail={'id': 'inverted_coordinates', 'message': 'xmin greater than xmax.'})
       
        if ((lat_coords[0] >= 0 and lat_coords[0] > lat_coords[1])
            or (lat_coords[0] < 0 and lat_coords[0] > lat_coords[1])):
            raise serializers.ValidationError(detail={'id': 'inverted_coordinates', 'message': 'ymin greater than ymax.'})
        
        # test lat long extents
        for lon in lon_coords:
            if (lon < -180 or lon > 180):
                detail={'id': 'invalid_longitude', 'message': 'Invalid longitude coordinate: {0}'.format(lon)}
                raise serializers.ValidationError(detail)
        for lat in lat_coords:
            if (lat < -90 and lat > 90):
                detail={'id': 'invalid_latitude', 'message': 'Invalid latitude coordinate: {0}'.format(lat)}
                raise serializers.ValidationError(detail)
        
        return (xmin, ymin, xmax, ymax)
    except MultiValueDictKeyError as e:
        param = e.message.replace("'",'')
        detail={'id': 'missing_parameter', 'message': 'Missing parameter: {0}'.format(param), 'param': param}
        raise serializers.ValidationError(detail)
   
def validate_string_field(name=None, data=None):
    detail={'id': 'missing_parameter', 'message': 'Missing parameter: {0}'.format(name), 'param': name}
    try:
        value = data[name]
        if value == None or value == '':
            raise serializers.ValidationError(detail)
        else:
            return value
    except Exception:
        raise serializers.ValidationError(detail)