"""
Provides serialization for API responses.

See `DRF serializer documentation  <http://www.django-rest-framework.org/api-guide/serializers/>`_
Used by the View classes api/views.py to serialize API responses as JSON or HTML.
See DEFAULT_RENDERER_CLASSES setting in core.settings.contrib for the enabled renderers.
"""
# -*- coding: utf-8 -*-
import json
import logging
import os
from collections import OrderedDict


from django.db import transaction
from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry
from django.utils import timezone
from django.utils.translation import ugettext as _
import django.core.exceptions

from rest_framework import serializers
from rest_framework_gis import serializers as geo_serializers

from jobs.models import (
    Job, HDXExportRegion
)
from tasks.models import (
    ExportRun, ExportTask
)
from utils import FORMAT_NAMES




# Get an instance of a logger
LOG = logging.getLogger(__name__)

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


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ('id', 'uid', 'user', 'name',
                  'description', 'event', 'export_formats', 'published',
                  'the_geom', 'feature_selection','buffer_aoi','exports','configurations','tags', 'extent')


    # TODO delete me below here soon
    exports = serializers.SerializerMethodField()
    def get_exports(self, obj):
        return map(lambda x: {'name':x},obj.export_formats)

    tags = serializers.SerializerMethodField()
    def get_tags(self, obj):
        return []

    configurations = serializers.SerializerMethodField()
    def get_configurations(self, obj):
        return []

    extent = serializers.SerializerMethodField()
    def get_extent(self, obj):
        return {
            'type':'Feature',
            'geometry':json.loads(obj.the_geom.json),
            'properties':{}
        }



def validate_model(model):
    try:
        model.full_clean()
    except django.core.exceptions.ValidationError as e:
        raise serializers.ValidationError(e.message_dict)

class HDXExportRegionSerializer(serializers.ModelSerializer): # noqa
    # Internally, an export region is a job model + an export region model
    # but to the UI, it appears as a single entity

    # hint to DRF these fields on creation
    export_formats = serializers.ListField()
    dataset_prefix = serializers.CharField()
    feature_selection = serializers.CharField()
    the_geom = geo_serializers.GeometryField()
    name = serializers.CharField()
    buffer_aoi = serializers.BooleanField()


    class Meta: # noqa
        model = HDXExportRegion
        fields = ('id', 'dataset_prefix', 'datasets', 'feature_selection',
                  'schedule_period', 'schedule_hour', 'export_formats', 'runs',
                  'locations', 'name', 'last_run', 'next_run', 'the_geom',
                  'dataset_prefix', 'job', 'license', 'subnational',
                  'extra_notes', 'is_private', 'buffer_aoi',)


    def create(self, validated_data): # noqa
        def slice_dict(in_dict,wanted_keys):
            return dict((k, in_dict[k]) for k in wanted_keys if k in in_dict)

        job_dict = slice_dict(validated_data,['the_geom','export_formats',
                                              'feature_selection','buffer_aoi'])
        job_dict['user'] = self.context['request'].user
        job_dict['name'] = validated_data.get('dataset_prefix')
        job_dict['description'] = validated_data.get('name')

        region_dict = slice_dict(validated_data,['extra_notes','is_private','locations',
                                                 'license','schedule_period','schedule_hour',
                                                 'subnational'])
        job = Job(**job_dict)
        validate_model(job)
        with transaction.atomic():
            job.save()
            region_dict['job'] = job
            region = HDXExportRegion(**region_dict)
            validate_model(region)
            region.save()
        return region


    def update(self, instance, validated_data): # noqa
        def update_attrs(model,v_data,keys):
            for key in keys:
                if key in v_data:
                    setattr(model,key,v_data[key])

        job = instance.job
        update_attrs(job,validated_data,['the_geom','export_formats',
                                         'feature_selection','buffer_aoi'])
        job.name = validated_data.get('dataset_prefix')
        job.description = validated_data.get('name')

        validate_model(job)
        update_attrs(instance,validated_data,['extra_notes','is_private','locations',
                                              'license','schedule_period','schedule_hour','subnational'])
        validate_model(instance)
        with transaction.atomic():
            instance.save()
            job.save()
        return instance
