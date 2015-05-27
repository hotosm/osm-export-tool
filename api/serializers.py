import logging
import pdb
from uuid import UUID
from rest_framework import serializers
from rest_framework.reverse import reverse
from datetime import datetime
from jobs.models import Job, ExportFormat, Region
from django.contrib.auth.models import User, Group
from django.contrib.gis.geos import GEOSGeometry, Polygon, GEOSException
from django.utils import timezone
from rest_framework_gis import serializers as geo_serializers
from django.utils.datastructures import MultiValueDictKeyError


try:
    from collections import OrderedDict
# python 2.6
except ImportError:
    from ordereddict import OrderedDict

# Get an instance of a logger
logger = logging.getLogger(__name__)

"""
class GroupSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()


class UserGroupSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    groups = GroupSerializer(many=True)
"""


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    
    
class RegionSerializer(geo_serializers.GeoFeatureModelSerializer):
    """
    Serializer returning GeoJSON representation of Regions.
    """
    url = serializers.HyperlinkedIdentityField(
       view_name='api:regions-detail',
       lookup_field='uid'
    )
    
    id = serializers.SerializerMethodField()
    
    class Meta:
        model = Region
        geo_field = 'the_geom'
        fields = ('id', 'uid','name','description', 'url','the_geom')
        
    def get_id(self, obj):
        return obj.uid
 

class SimpleRegionSerializer(serializers.ModelSerializer):
    """
    Serializer for returning Region data without geometry.
    """
    
    url = serializers.HyperlinkedIdentityField(
       view_name='api:regions-detail',
       lookup_field='uid'
    )
    
    class Meta:
        model = Region
        fields = ('uid','name','description', 'url')
    


class ExportFormatSerializer(serializers.ModelSerializer):
    """
    Representation of ExportFormat.
    """
    
    url = serializers.HyperlinkedIdentityField(
       view_name='api:formats-detail',
       lookup_field='slug'
    )
    
    class Meta:
        model = ExportFormat
        fields = ('uid', 'url', 'name', 'description')
        

class JobSerializer(serializers.HyperlinkedModelSerializer):
    """
    Job Serializer.
    """
    formats = ExportFormatSerializer(many=True)
    region = SimpleRegionSerializer()

    url = serializers.HyperlinkedIdentityField(
        view_name = 'api:jobs-detail',
        lookup_field = 'uid'
    )
    
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Job
        fields = ('uid', 'name', 'url', 'description', 'region', 'formats',
                  'created_at', 'updated_at', 'status', 'user')

    def to_internal_value(self, data):
        request = self.context['request']
        user = request.user
        job_name = _validate_string_field('name', data)
        description = _validate_string_field('description', data)
        extents = _validate_bbox_params(data)
        bbox = _validate_bbox_extents(extents)
        formats = _validate_formats(request)
        the_geom = GEOSGeometry(bbox, srid=4326)
        the_geog = GEOSGeometry(bbox)
        the_geom_webmercator = the_geom.transform(ct=3857, clone=True)
        
        # lookup job region here
        region = Region.objects.filter(the_geom__contains=the_geom)[0]
        logger.debug(region)
        return {'name': job_name, 'description': description, 'region': region, 'user': user,
                'the_geom': the_geom, 'the_geom_webmercator': the_geom_webmercator, 'the_geog': the_geog}
    

# validators

def _validate_formats(request):
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
            val = UUID(format, version=4)
        except ValueError:
            raise serializers.ValidationError(detail = {'id': invalid_id,
            'message': invalid_message,
            'formats_url': formats_url
        })
    
    
    

def _validate_bbox_extents(extents):
    try:
        bbox = Polygon.from_bbox(extents)
        if (bbox.valid):
            return bbox
        else:
            raise serializers.ValidationError(detail={'id': 'invalid_bounds', 'message': 'Invalid bounding box.'})
    except GEOSException as e:
        logger.debug(e)
        raise serializers.ValidationError(detail={'id': 'invalid_bounds', 'message': 'Invalid bounding box.'}) 

def _validate_bbox_params(data):
    try:
        xmin = data['xmin']
        ymin = data['ymin']
        xmax = data['xmax']
        ymax = data['ymax']
        return (xmin, ymin, xmax, ymax)
    except MultiValueDictKeyError as e:
        param = e.message.replace("'",'')
        detail={'id': 'missing_parameter', 'message': 'Missing parameter: {0}'.format(param), 'param': param}
        raise serializers.ValidationError(detail)
   
def _validate_string_field(name=None, data=None):
    detail={'id': 'missing_parameter', 'message': 'Missing parameter: {0}'.format(name), 'param': name}
    try:
        value = data[name]
        if value == None or value == '':
            raise serializers.ValidationError(detail)
        else:
            return value
    except Exception:
        raise serializers.ValidationError(detail)