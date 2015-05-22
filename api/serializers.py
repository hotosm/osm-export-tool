import logging
import pdb
from rest_framework import serializers
from datetime import datetime
from jobs.models import Job, ExportFormat
from django.contrib.auth.models import User, Group
from django.contrib.gis.geos import GEOSGeometry
from django.utils import timezone


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


class ExportFormatSerializer(serializers.ModelSerializer):
    
    url = serializers.HyperlinkedIdentityField(
       view_name='api:formats-detail',
       lookup_field='slug'
    )
    
    class Meta:
        model = ExportFormat
        fields = ('uid', 'url', 'name', 'description')
        

class JobSerializer(serializers.HyperlinkedModelSerializer):
    """
    Job Serializer
    """
    
    formats = ExportFormatSerializer(many=True)

    url = serializers.HyperlinkedIdentityField(
        view_name = 'api:jobs-detail',
        lookup_field = 'uid'
    )

    class Meta:
        model = Job
        fields = ('uid', 'name', 'url', 'description', 'formats',
                  'created_at', 'updated_at', 'status')

    def to_internal_value(self, data):
        request = self.context['request']
        user = request.user
        job_name = data['name']
        description = data['description']
        bbox_wkt = data['bbox']
        logger.debug(bbox_wkt)
        the_geom = GEOSGeometry(bbox_wkt, srid=4326)
        the_geog = GEOSGeometry(bbox_wkt)
        the_geom_webmercator = the_geom.transform(ct=3857, clone=True)
        return {'name': job_name, 'description': description, 'user': user,
                'the_geom': the_geom, 'the_geom_webmercator': the_geom_webmercator, 'the_geog': the_geog}
