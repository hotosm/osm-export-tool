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
from hot_exports import settings
from .validators import *

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
        job_name = validate_string_field('name', data)
        description = validate_string_field('description', data)
        formats = validate_formats(request)
        extents = validate_bbox_params(data)
        bbox = validate_bbox(extents)
        the_geom = GEOSGeometry(bbox, srid=4326)
        the_geog = GEOSGeometry(bbox)
        the_geom_webmercator = the_geom.transform(ct=3857, clone=True)
        
        """
        Find the regions which intersect with the job.
        Calculate the intersection and return by area of intersection desc.
        """
        regions = Region.objects.filter(the_geom__intersects=the_geom).intersection(the_geom, field_name='the_geom').order_by( '-intersection')
        region = validate_region(regions)
        
        return {'name': job_name, 'description': description, 'region': region, 'user': user,
                'the_geom': the_geom, 'the_geom_webmercator': the_geom_webmercator, 'the_geog': the_geog}
