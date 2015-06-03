import logging
import magic
import StringIO
from collections import OrderedDict
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
        detail = OrderedDict()
        detail['id'] = 'invalid_region'
        detail['message'] = 'Job extent is not within a valid region.'
        raise serializers.ValidationError(detail)
    # region with largest area of intersection returned.
    return regions[0]

def validate_formats(request):
    scheme = request.scheme
    host = request.META['HTTP_HOST']
    formats_url = '{0}://{1}{2}'.format(scheme, host, reverse('api:formats-list'))
    missing = OrderedDict()
    invalid = OrderedDict()
    missing['id'] = 'missing_format'
    missing['message'] = 'Export format uid required.'
    missing['formats_url'] = formats_url
    invalid['id'] = 'invalid_format_uid'
    invalid['message'] = 'Invalid export format uid.'
    invalid['formats_url'] = formats_url
    formats = request.data.getlist('formats')
    if len(formats) == 0:
        raise serializers.ValidationError(missing)
    for format in formats:
        try:
            UUID(format, version=4)
        except ValueError:
            raise serializers.ValidationError(invalid)

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

def validate_bbox(extents):
    detail = OrderedDict()
    detail['id'] = 'invalid_bounds'
    detail['message'] = 'Invalid bounding box.'
    try:
        bbox = Polygon.from_bbox(extents)
        if (bbox.valid):
            if bbox.area > settings.JOB_MAX_EXTENT:
                detail['id'] = 'invalid_extents'
                detail['message'] = 'Job extents too large.'
                raise serializers.ValidationError(detail)
            return bbox
        else:
            raise serializers.ValidationError(detail)
    except GEOSException as e:
        raise serializers.ValidationError(detail) 

def validate_bbox_params(data):
    detail = OrderedDict()
    try:
        # test we have all params
        xmin = data['xmin']
        ymin = data['ymin']
        xmax = data['xmax']
        ymax = data['ymax']
        
        # test not empty
        for ex in [xmin, ymin, xmax, ymax]:
            if ex == None or ex == '':
                detail['id'] = 'empty_bbox_parameter'
                detail['message'] = 'Empty bounding box parameter.'
                raise serializers.ValidationError(detail)
        # test for number
        lon_coords = []
        lat_coords = []
        try: 
            lon_coords = [float(xmin), float(xmax)]
            lat_coords = [float(ymin), float(ymax)]
        except ValueError as e:
            val = e.message.split(':')[1]
            detail['id'] = 'invalid_coordinate'
            detail['message'] = 'Invalid coordinate: {0}'.format(val)
            raise serializers.ValidationError(detail)
        
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
        
        return (xmin, ymin, xmax, ymax)
    except MultiValueDictKeyError as e:
        param = e.message.replace("'",'')
        detail['id'] = 'missing_parameter'
        detail['message'] = 'Missing parameter: {0}'.format(param)
        detail['param'] = param
        raise serializers.ValidationError(detail)
   
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
    
def validate_upload(data, config_type):
    detail = OrderedDict()
    detail['id'] = 'missing_file'
    detail['message'] = 'No file uploaded.'
    try:
        upload = data['upload']
        if upload == None:
            raise serializers.ValidationError(detail)
        else:
            ACCEPT_MIME_TYPES = {'PRESET': ('application/xml', 'text/plain'),
                                'TRANSFORM': ('application/x-sql', 'text/plain'),
                                'TRANSLATION': ('text/plain',)}
        content_type = magic.from_buffer(upload.read(1024), mime=True)
        if (content_type not in ACCEPT_MIME_TYPES[config_type]):
            detail = OrderedDict()
            detail['id'] = 'invalid_content'
            detail['message'] = 'Uploaded config file has invalid content: {0}'.format(content_type)
            raise serializers.ValidationError(detail)
        return (upload, content_type)
    except Exception:
        raise serializers.ValidationError(detail)

def validate_config_type(name=None, data=None):
    detail = OrderedDict()
    detail['id'] = 'missing_parameter'
    detail['message'] = 'Missing parameter: {0}'.format(name)
    detail['param'] = name
    try:
        value = data[name]
        if value == None or value == '':
            raise serializers.ValidationError(detail)
        else:
            if value not in config_field.choices:
                return value
    except Exception:
        raise serializers.ValidationError(detail)
    
