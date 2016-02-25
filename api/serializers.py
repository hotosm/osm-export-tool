"""
Provides serialization for API responses.

See `DRF serializer documentation  <http://www.django-rest-framework.org/api-guide/serializers/>`_
Used by the View classes api/views.py to serialize API responses as JSON or HTML.
See DEFAULT_RENDERER_CLASSES setting in core.settings.contrib for the enabled renderers.
"""
# -*- coding: utf-8 -*-
import cPickle
import json
import logging

from rest_framework_gis import serializers as geo_serializers

from django.contrib.gis.geos import GEOSGeometry
from django.utils import timezone
from django.utils.translation import ugettext as _

from rest_framework import serializers

import validators
from jobs.models import (
    ExportConfig, ExportFormat, Job, Region, RegionMask, Tag
)
from tasks.models import (
    ExportRun, ExportTask, ExportTaskException, ExportTaskResult
)

try:
    from collections import OrderedDict
# python 2.6
except ImportError:
    from ordereddict import OrderedDict

# Get an instance of a logger
logger = logging.getLogger(__name__)


class TagSerializer(serializers.ModelSerializer):
    """Serialize the Tag model."""
    class Meta:
        model = Tag
        fields = ('key', 'value', 'data_model', 'geom_types')


class SimpleExportConfigSerializer(serializers.Serializer):
    """Return a sub-set of ExportConfig model attributes."""
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
    """Return the full set of ExportConfig model attributes."""
    uid = serializers.UUIDField(read_only=True)
    url = serializers.HyperlinkedIdentityField(
       view_name='api:configs-detail',
       lookup_field='uid'
    )
    name = serializers.CharField(max_length=255)
    config_type = serializers.ChoiceField(['PRESET', 'TRANSLATION', 'TRANSFORM'])
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
        """Create an ExportConfig instance."""
        return ExportConfig.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Update an ExportConfig instance."""
        instance.config_type = validated_data.get('config_type', instance.config_type)
        instance.upload.delete(False)  # delete the old file..
        instance.upload = validated_data.get('upload', instance.upload)
        instance.name = validated_data.get('name', instance.name)
        instance.filename = validated_data.get('filename', instance.filename)
        instance.content_type = validated_data.get('content_type', instance.content_type)
        instance.updated_at = timezone.now()
        instance.save()
        return instance

    def validate(self, data):
        """Validate the form data."""
        logger.debug(data)
        upload = data['upload']
        config_type = data['config_type']
        content_type = validators.validate_content_type(upload, config_type)
        if config_type == 'PRESET':
            validators.validate_preset(upload)
        data['content_type'] = content_type
        fname = data['upload'].name
        data['filename'] = fname.replace(' ', '_').lower()
        return data

    def get_size(self, obj):
        size = obj.upload.size
        return size

    def get_created(self, obj):
        return obj.created_at

    def get_owner(self, obj):
        return obj.user.username


class ExportTaskResultSerializer(serializers.ModelSerializer):
    """Serialize ExportTaskResult models."""
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
    """Serialize ExportTaskExceptions."""
    exception = serializers.SerializerMethodField()

    class Meta:
        model = ExportTaskException
        fields = ('exception',)

    def get_exception(self, obj):
        exc_info = cPickle.loads(str(obj.exception)).exc_info
        return str(exc_info[1])


class ExportTaskSerializer(serializers.ModelSerializer):
    """Serialize ExportTasks models."""
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
        """Serialize the ExportTaskResult for this ExportTask."""
        try:
            result = obj.result
            serializer = ExportTaskResultSerializer(result, many=False, context=self.context)
            return serializer.data
        except ExportTaskResult.DoesNotExist as e:
            return None  # no result yet

    def get_errors(self, obj):
        """Serialize the ExportTaskExceptions for this ExportTask."""
        try:
            errors = obj.exceptions
            serializer = ExportTaskExceptionSerializer(errors, many=True, context=self.context)
            return serializer.data
        except ExportTaskException.DoesNotExist as e:
            return None

    def get_started_at(self, obj):
        if (not obj.started_at):
            return None  # not started yet
        else:
            return obj.started_at

    def get_finished_at(self, obj):
        if (not obj.finished_at):
            return None  # not finished yet
        else:
            return obj.finished_at

    def get_duration(self, obj):
        """Get the duration for this ExportTask."""
        started = obj.started_at
        finished = obj.finished_at
        if started and finished:
            return str(finished - started)
        else:
            return None  # can't compute yet


class SimpleJobSerializer(serializers.Serializer):
    """Return a sub-set of Job model attributes."""
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
        """Return the Job's extent as a GeoJSON Feature."""
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
    """Serialize ExportRun."""
    url = serializers.HyperlinkedIdentityField(
       view_name='api:runs-detail',
       lookup_field='uid'
    )
    job = SimpleJobSerializer()  # nest the job details
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
        """Return the duration of the the run."""
        started = obj.started_at
        finished = obj.finished_at
        if started and finished:
            return str(finished - started)
        else:
            return None

    def get_user(self, obj):
        return obj.user.username


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class RegionMaskSerializer(geo_serializers.GeoFeatureModelSerializer):
    """Return a GeoJSON representation of the region mask."""
    class Meta:
        model = RegionMask
        geo_field = 'the_geom'
        fields = ('the_geom',)


class RegionSerializer(geo_serializers.GeoFeatureModelSerializer):
    """Serializer returning GeoJSON representation of Regions."""
    url = serializers.HyperlinkedIdentityField(
       view_name='api:regions-detail',
       lookup_field='uid'
    )
    id = serializers.SerializerMethodField()

    class Meta:
        model = Region
        geo_field = 'the_geom'
        fields = ('id', 'uid', 'name', 'description', 'url', 'the_geom')

    def get_id(self, obj):
        return obj.uid


class SimpleRegionSerializer(serializers.ModelSerializer):
    """Serializer for returning Region model data without geometry."""
    url = serializers.HyperlinkedIdentityField(
       view_name='api:regions-detail',
       lookup_field='uid'
    )

    class Meta:
        model = Region
        fields = ('uid', 'name', 'description', 'url')


class ExportFormatSerializer(serializers.ModelSerializer):
    """Return a representation of the ExportFormat model."""
    url = serializers.HyperlinkedIdentityField(
       view_name='api:formats-detail',
       lookup_field='slug'
    )

    class Meta:
        model = ExportFormat
        fields = ('uid', 'url', 'slug', 'name', 'description')


class ListJobSerializer(serializers.Serializer):
    """
    Return a sub-set of Job model attributes.

    Provides a stripped down set of export attributes.
    Removes the selected Tags from the Job representation.
    Used to display the list of exports in the export browser
    where tag info is not required.
    """
    uid = serializers.SerializerMethodField()
    url = serializers.HyperlinkedIdentityField(
        view_name='api:jobs-detail',
        lookup_field='uid'
    )
    name = serializers.CharField()
    description = serializers.CharField()
    event = serializers.CharField()
    created_at = serializers.DateTimeField(read_only=True)
    owner = serializers.SerializerMethodField(read_only=True)
    extent = serializers.SerializerMethodField()
    region = SimpleRegionSerializer(read_only=True)
    published = serializers.BooleanField()

    def get_uid(self, obj):
        return obj.uid

    def get_extent(self, obj):
        """Return the export extent as a GeoJSON Feature."""
        uid = str(obj.uid)
        name = obj.name
        geom = obj.the_geom
        geometry = json.loads(GEOSGeometry(geom).geojson)
        feature = OrderedDict()
        feature['type'] = 'Feature'
        feature['properties'] = {'uid': uid, 'name': name}
        feature['geometry'] = geometry
        return feature

    def get_owner(self, obj):
        return obj.user.username


class JobSerializer(serializers.Serializer):
    """
    Return a full representation of an export Job.

    This is the core representation of the API.
    """

    """
    List of the available Export Formats.
    
    This list should be updated to add support for
    additional export formats.
    """
    EXPORT_FORMAT_CHOICES = (
        ('pbf', 'OSM PBF'),
        ('shp', 'Shapefile Format'),
        ('obf', 'OBF Format'),
        ('kml', 'KML Format'),
        ('garmin', 'Garmin Format'),
        ('sqlite', 'SQLITE Format'),
        ('thematic', 'Thematic Shapefile Format')
    )

    formats = serializers.MultipleChoiceField(
        choices=EXPORT_FORMAT_CHOICES,
        allow_blank=False,
        write_only=True,
        error_messages={
            'invalid_choice': _("invalid export format."),
            'not_a_list': _('Expected a list of items but got type "{input_type}".')
        }
    )

    uid = serializers.UUIDField(read_only=True)
    url = serializers.HyperlinkedIdentityField(
        view_name='api:jobs-detail',
        lookup_field='uid'
    )
    name = serializers.CharField(
        max_length=100,
    )
    description = serializers.CharField(
        max_length=255,
    )
    event = serializers.CharField(
        max_length=100,
        allow_blank=True,
        required=False
    )
    created_at = serializers.DateTimeField(read_only=True)
    owner = serializers.SerializerMethodField(read_only=True)
    exports = serializers.SerializerMethodField()
    configurations = serializers.SerializerMethodField()
    published = serializers.BooleanField(required=False)
    feature_save = serializers.BooleanField(required=False)
    feature_pub = serializers.BooleanField(required=False)
    xmin = serializers.FloatField(
        max_value=180, min_value=-180, write_only=True,
        error_messages={
            'required': _('xmin is required.'),
            'invalid': _('invalid xmin value.'),
        }
    )
    ymin = serializers.FloatField(
        max_value=90, min_value=-90, write_only=True,
        error_messages={
            'required': _('ymin is required.'),
            'invalid': _('invalid ymin value.'),
        }
    )
    xmax = serializers.FloatField(
        max_value=180, min_value=-180, write_only=True,
        error_messages={
            'required': _('xmax is required.'),
            'invalid': _('invalid xmax value.'),
        }
    )
    ymax = serializers.FloatField(
        max_value=90, min_value=-90, write_only=True,
        error_messages={
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
        """Creates an export Job."""
        return Job.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Not implemented as Jobs are cloned rather than updated."""
        pass

    def validate(self, data):
        """
        Validates the data submitted during Job creation.

        See api/validators.py for validation code.
        """
        user = data['user']
        validators.validate_formats(data)
        extents = validators.validate_bbox_params(data)
        the_geom = validators.validate_bbox(extents, user=user)
        data['the_geom'] = the_geom
        regions = Region.objects.filter(the_geom__intersects=the_geom).intersection(the_geom, field_name='the_geom')
        # sort the returned regions by area of intersection, largest first.
        sorted_regions = sorted(regions.all(), key=lambda a: a.intersection.area, reverse=True) 
        data['region'] = validators.validate_region(sorted_regions)
        # remove unwanted fields, these are pulled from the request in the view if the serializer is valid
        data.pop('xmin'), data.pop('ymin'), data.pop('xmax'), data.pop('ymax'), data.pop('formats')
        return data

    def get_extent(self, obj):
        """Return the export extent as a GeoJSON Feature."""
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
        """Return the export formats selected for this export."""
        formats = [format for format in obj.formats.all()]
        serializer = ExportFormatSerializer(formats, many=True, context={'request': self.context['request']})
        return serializer.data

    def get_configurations(self, obj):
        """Return the configurations selected for this export."""
        configs = obj.configs.all()
        serializer = SimpleExportConfigSerializer(configs, many=True,
                                                  context={'request': self.context['request']})
        return serializer.data

    def get_tags(self, obj):
        """Return the Tags selected for this export."""
        tags = obj.tags.all()
        serializer = TagSerializer(tags, many=True)
        return serializer.data

    def get_owner(self, obj):
        """Return the username for the owner of this export."""
        return obj.user.username
