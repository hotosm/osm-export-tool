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
import os

from rest_framework.reverse import reverse
from rest_framework_gis import serializers as geo_serializers

from django.db import transaction
from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry
from django.utils import timezone
from django.utils.translation import ugettext as _

from rest_framework import serializers

import validators
from jobs.models import (
    ExportConfig, Job, Tag, HDXExportRegion
)
from tasks.models import (
    ExportRun, ExportTask
)
from utils import FORMAT_NAMES

try:
    from collections import OrderedDict
# python 2.6
except ImportError:
    from ordereddict import OrderedDict


from feature_selection.feature_selection import FeatureSelection

# Get an instance of a logger
LOG = logging.getLogger(__name__)


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
    config_type = serializers.ChoiceField(['PRESET'])
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


class ExportTaskSerializer(serializers.ModelSerializer):
    """Serialize ExportTasks models."""
    errors = serializers.SerializerMethodField()
    started_at = serializers.SerializerMethodField()
    finished_at = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    url = serializers.HyperlinkedIdentityField(
       view_name='api:tasks-detail',
       lookup_field='uid'
    )
    download_url = serializers.SerializerMethodField()


    class Meta:
        model = ExportTask
        fields = ('uid', 'url', 'name', 'status', 'started_at', 'finished_at', 'duration', 'errors','description','filesize_bytes','filenames','download_url')

    def get_description(self,obj):
        if obj.name in FORMAT_NAMES:
            return FORMAT_NAMES[obj.name].description
        return ""

    def get_errors(self, obj):
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

    def get_download_url(self, obj):
        download_media_root = settings.EXPORT_MEDIA_ROOT
        if obj.filenames:
            filename = obj.filenames[0] #TODO make me work with multiple URLs
            return os.path.join(download_media_root,str(obj.run.uid), filename)
        return None

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


class SimplestJobSerializer(serializers.ModelSerializer):
    """Return a sub-set of Job model attributes."""

    class Meta:
        model = Job
        fields = ('uid', 'name',)


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
    formats = serializers.MultipleChoiceField(
        choices=FORMAT_NAMES.keys(),
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
        data['export_formats'] = list(data['formats'])
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
        return [{
            'slug': slug,
            'description': FORMAT_NAMES[slug].description,
            'url': reverse('api:formats-detail', args=[slug], request=self.context['request']),
        } for slug in obj.export_formats]

    def get_configurations(self, obj):
        """Return the configurations selected for this export."""
        configs = [obj.config]
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


class HDXExportRegionSerializer(serializers.ModelSerializer): # noqa
    dataset_prefix = serializers.RegexField('^[a-z0-9-_]+$')
    export_formats = serializers.MultipleChoiceField(
        choices=HDXExportRegion.EXPORT_FORMAT_CHOICES)
    feature_selection = serializers.CharField()
    job = SimplestJobSerializer(read_only=True)
    name = serializers.CharField()
    the_geom = geo_serializers.GeometryField()
    buffer_aoi = serializers.BooleanField(default=False)

    class Meta: # noqa
        model = HDXExportRegion
        fields = ('id', 'dataset_prefix', 'datasets', 'feature_selection',
                  'schedule_period', 'schedule_hour', 'export_formats', 'runs',
                  'locations', 'name', 'last_run', 'next_run', 'the_geom',
                  'dataset_prefix', 'job', 'license', 'subnational',
                  'extra_notes', 'is_private', 'buffer_aoi',)

    def validate(self, data): # noqa
        f = FeatureSelection(data.get('feature_selection'))

        if not f.valid:
            raise serializers.ValidationError({
                'feature_selection': f.errors
            })

        return data

    def create(self, validated_data): # noqa
        LOG.info('validated_data: {}'.format(validated_data))
        with transaction.atomic():
            request = self.context['request']

            job = Job.objects.create(
                the_geom=validated_data.get('the_geom'),
                name=validated_data.get('dataset_prefix'),
                export_formats=list(validated_data.get('export_formats')),
                description=validated_data.get('name'),
                feature_selection=validated_data.get('feature_selection'),
                user=request.user,
                buffer_aoi=validated_data.get('buffer_aoi'),
            )

            region = HDXExportRegion.objects.create(
                extra_notes=validated_data.get('extra_notes'),
                is_private=validated_data.get('is_private') or False,
                locations=validated_data.get('locations'),
                license=validated_data.get('license'),
                schedule_period=validated_data.get('schedule_period'),
                schedule_hour=validated_data.get('schedule_hour'),
                subnational=validated_data.get('subnational'),
                job=job,
            )
        return region

    def update(self, instance, validated_data): # noqa
        with transaction.atomic():
            job = instance.job
            job.name = validated_data.get('dataset_prefix')
            job.the_geom = validated_data.get('the_geom')
            job.export_formats = list(validated_data.get('export_formats'))
            job.feature_selection = validated_data.get('feature_selection')
            job.description = validated_data.get('name')
            job.buffer_aoi = validated_data.get('buffer_aoi')
            job.save()

            instance.extra_notes = validated_data.get('extra_notes')
            instance.is_private = validated_data.get('is_private') or False
            instance.locations = validated_data.get('locations')
            instance.license = validated_data.get('license')
            instance.schedule_period = validated_data.get('schedule_period')
            instance.schedule_hour = validated_data.get('schedule_hour')
            instance.subnational = validated_data.get('subnational') or False
            instance.save()
        return instance
