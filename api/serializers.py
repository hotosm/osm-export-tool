import logging
import pdb
import json
import cPickle
from uuid import UUID
from rest_framework import serializers
from rest_framework.reverse import reverse
from rest_framework.utils import html
from datetime import datetime, timedelta
from jobs.models import Job, ExportFormat, Region, RegionMask, ExportConfig, Tag
from tasks.models import ExportRun, ExportTask, ExportTaskResult, ExportTaskException
from django.contrib.auth.models import User, Group
from django.contrib.gis.geos import GEOSGeometry, Polygon, GEOSException
from django.contrib.gis.measure import A
from django.utils.translation import ugettext as _
from django.utils import timezone
from rest_framework_gis import serializers as geo_serializers
from rest_framework_gis import fields as geo_fields
from django.utils.datastructures import MultiValueDictKeyError
from hot_exports import settings
import validators
import six


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

class TagSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Tag
        fields = ('key', 'value', 'data_model', 'geom_types')


class SimpleExportConfigSerializer(serializers.Serializer):
    uid = serializers.UUIDField(read_only=True)
    name = serializers.CharField()
    config_type = serializers.CharField()
    filename = serializers.CharField()
    published = serializers.BooleanField()
    created = serializers.SerializerMethodField()
    url = serializers.HyperlinkedIdentityField(
       view_name='api:configs-detail',
       lookup_field='uid'
    )
    
    def get_created(self, obj):
        return obj.created_at


class ExportConfigSerializer(serializers.Serializer):
    uid = serializers.UUIDField(read_only=True)
    url = serializers.HyperlinkedIdentityField(
       view_name='api:configs-detail',
       lookup_field='uid'
    )
    name = serializers.CharField(max_length=255)
    config_type = serializers.ChoiceField(['PRESET','TRANSLATION','TRANSFORM'])
    filename = serializers.CharField(max_length=255, read_only=True, default='')
    size = serializers.SerializerMethodField()
    content_type = serializers.CharField(max_length=50, read_only=True)
    upload = serializers.FileField(allow_empty_file=False, max_length=100)
    published = serializers.BooleanField()
    created = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField(read_only=True)
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    
    def create(self, validated_data):
        logger.debug(validated_data)
        return ExportConfig.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        instance.config_type = validated_data.get('config_type', instance.config_type)
        instance.upload.delete(False) # delete the old file..
        instance.upload = validated_data.get('upload', instance.upload)
        instance.name = validated_data.get('name', instance.name)
        instance.filename = validated_data.get('filename', instance.filename)
        instance.content_type = validated_data.get('content_type', instance.content_type)
        instance.updated_at = timezone.now()
        instance.save()
        return instance
    
    def validate(self, data):
        logger.debug(data)
        upload = data['upload']
        config_type = data['config_type']
        content_type = validators.validate_content_type(upload, config_type)
        data['content_type'] = content_type
        fname = data['upload'].name
        data['filename'] = fname.replace(' ','_').lower()
        return data
    
    def get_size(self, obj):
        size = obj.upload.size
        return size
    
    def get_created(self, obj):
        return obj.created_at
    
    def get_owner(self, obj):
        return obj.user.username;

    

class ExportTaskResultSerializer(serializers.ModelSerializer):
    
    url = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    class Meta:
        model = ExportTaskResult
        fields = ('filename', 'size', 'url',)
    
    def get_url(self, obj):
        request = self.context['request']
        return request.build_absolute_uri(obj.download_url)
    
    def get_size(self, obj):
        return "{0:.3f} MB".format(obj.size)


class ExportTaskExceptionSerializer(serializers.ModelSerializer):
    
    exception = serializers.SerializerMethodField()
    
    class Meta:
        model = ExportTaskException
        fields = ('exception',)
        
    def get_exception(self, obj):
        exc_info = cPickle.loads(str(obj.exception)).exc_info
        return str(exc_info[1])
    

class ExportTaskSerializer(serializers.ModelSerializer):
    result = serializers.SerializerMethodField()
    errors = serializers.SerializerMethodField()
    started_at = serializers.SerializerMethodField()
    finished_at = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    url = serializers.HyperlinkedIdentityField(
       view_name='api:tasks-detail',
       lookup_field='uid'
    )
    
    class Meta:
        model = ExportTask
        fields = ('uid', 'url', 'name', 'status', 'started_at', 'finished_at', 'duration', 'result', 'errors',)

    def get_result(self, obj):
        try:
            result = obj.result
            serializer = ExportTaskResultSerializer(result, many=False, context=self.context)
            return serializer.data
        except ExportTaskResult.DoesNotExist as e:
            return None # no result yet
    
    def get_errors(self, obj):
        try:
            errors = obj.exceptions
            serializer = ExportTaskExceptionSerializer(errors, many=True, context=self.context)
            return serializer.data
        except ExportTaskException.DoesNotExist as e:
            return None
    
    def get_started_at(self, obj):
        if (not obj.started_at):
            return None # not started yet
        else:
            return obj.started_at
    
    def get_finished_at(self, obj):
        if (not obj.finished_at):
            return None # not finished yet
        else:
            return obj.finished_at
        
    def get_duration(self, obj):
        started = obj.started_at
        finished = obj.finished_at
        if started and finished:
            return  str(finished - started)
        else:
            return None # can't compute yet


class SimpleJobSerializer(serializers.Serializer):
    uid = serializers.SerializerMethodField()
    name = serializers.CharField()
    description = serializers.CharField()
    url = serializers.HyperlinkedIdentityField(
       view_name='api:jobs-detail',
       lookup_field='uid'
    )
    extent = serializers.SerializerMethodField()
    
    def get_uid(self, obj):
        return obj.uid
    
    def get_extent(self, obj):
        uid = str(obj.uid)
        name = obj.name
        geom = obj.the_geom
        geometry = json.loads(GEOSGeometry(geom).geojson)
        feature = OrderedDict()
        feature['type'] = 'Feature'
        feature['properties'] = {'uid': uid, 'name': name}
        feature['geometry'] = geometry
        return feature


class ExportRunSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
       view_name='api:runs-detail',
       lookup_field='uid'
    )
    job = SimpleJobSerializer()
    tasks = ExportTaskSerializer(many=True)
    finished_at = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    class Meta:
        model = ExportRun
        fields = ('uid', 'url', 'started_at', 'finished_at', 'duration', 'user', 'status', 'job', 'tasks')
    
    def get_finished_at(self, obj):
        if (not obj.finished_at):
            return {}
        else:
            return obj.finished_at
    
    def get_duration(self, obj):
        started = obj.started_at
        finished = obj.finished_at
        if started and finished:
            return  str(finished - started)
        else:
            return None
    
    def get_user(self, obj):
        return obj.user.username


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    

class RegionMaskSerializer(geo_serializers.GeoFeatureModelSerializer):
    """
    Returns a GeoJSON representation of the region mask.
    """
    class Meta:
        model = RegionMask
        geo_field = 'the_geom'
        fields = ('the_geom',)
    
    
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
        fields = ('uid', 'url', 'slug', 'name', 'description')   


class JobSerializer(serializers.Serializer):
    """
    Job Serializer.
    """
    """
    Would prefer if these were loaded at runtime,
    but the MultipleChoiceField loads data from non-test db during tests.
    """
    EXPORT_FORMAT_CHOICES = (
        ('shp', 'Shapefile Format'),
        ('obf', 'OBF Format'),
        ('kml', 'KML Format'),
        ('garmin', 'Garmin Format'),
        ('sqlite', 'SQLITE Format'),
        ('thematic','Thematic Shapefile Format')
    )
    
    formats = serializers.MultipleChoiceField(
        choices = EXPORT_FORMAT_CHOICES,
        allow_blank = False,
        write_only = True,
        error_messages = {
            'invalid_choice': _("invalid export format."),
            'not_a_list': _('Expected a list of items but got type "{input_type}".')
        }
    )

    uid = serializers.UUIDField(read_only=True)
    url = serializers.HyperlinkedIdentityField(
        view_name = 'api:jobs-detail',
        lookup_field = 'uid'
    )
    name = serializers.CharField(
        max_length=100,
    )
    description = serializers.CharField(
        max_length=255,
    )
    event = serializers.CharField(
        max_length=100,
        allow_blank=True
    )
    created_at = serializers.DateTimeField(read_only=True)
    owner = serializers.SerializerMethodField(read_only=True)
    exports = serializers.SerializerMethodField()
    configurations = serializers.SerializerMethodField()
    published = serializers.BooleanField(required=False)
    feature_save = serializers.BooleanField(required=False)
    feature_pub = serializers.BooleanField(required=False)
    #configs = ExportConfigSerializer(many=True)
    xmin = serializers.FloatField(
        max_value=180, min_value=-180, write_only=True,
        error_messages = {
            'required': _('xmin is required.'),
            'invalid': _('invalid xmin value.'),
        }                     
    )
    ymin = serializers.FloatField(
        max_value=90, min_value=-90, write_only=True,
        error_messages = {
            'required': _('ymin is required.'),
            'invalid': _('invalid ymin value.'),
        }  
    )
    xmax = serializers.FloatField(
        max_value=180, min_value=-180, write_only=True,
        error_messages = {
            'required': _('xmax is required.'),
            'invalid': _('invalid xmax value.'),
        }  
    )
    ymax = serializers.FloatField(
        max_value=90, min_value=-90, write_only=True,
        error_messages = {
            'required': _('ymax is required.'),
            'invalid': _('invalid ymax value.'),
        }  
    )
    region = SimpleRegionSerializer(read_only=True)
    extent = serializers.SerializerMethodField(read_only=True)
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    tags = serializers.SerializerMethodField()
    
    def create(self, validated_data):
        return Job.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        pass
    
    def validate(self, data):
        user = data['user']
        validators.validate_formats(data)
        extents = validators.validate_bbox_params(data)
        bbox = validators.validate_bbox(extents, user=user)
        the_geom = GEOSGeometry(bbox, srid=4326)
        data['the_geom'] = the_geom
        regions = Region.objects.filter(the_geom__intersects=the_geom).intersection(the_geom, field_name='the_geom')
        sorted_regions =  sorted(regions.all(), key=lambda a: a.intersection.area, reverse=True) # order by largest area of intersection
        data['region'] = validators.validate_region(sorted_regions)
        # remove unwanted fields
        data.pop('xmin'),  data.pop('ymin'), data.pop('xmax'), data.pop('ymax'), data.pop('formats')
        return data
    
    def get_extent(self, obj):
        uid = str(obj.uid)
        name = obj.name
        geom = obj.the_geom
        geometry = json.loads(GEOSGeometry(geom).geojson)
        feature = OrderedDict()
        feature['type'] = 'Feature'
        feature['properties'] = {'uid': uid, 'name': name}
        feature['geometry'] = geometry
        return feature
    
    def get_exports(self, obj):
        formats = [format for format in obj.formats.all()]
        serializer = ExportFormatSerializer(formats, many=True, context={'request': self.context['request']})
        return serializer.data
    
    def get_configurations(self, obj):
        configs = obj.configs.all()
        serializer = SimpleExportConfigSerializer(configs, many=True,
                                                  context={'request': self.context['request']})
        return serializer.data
    
    def get_tags(self, obj):
        tags = obj.tags.all()
        serializer = TagSerializer(tags, many=True)
        return serializer.data
    
    def get_owner(self, obj):
        return obj.user.username;
    