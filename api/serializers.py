"""
Provides serialization for API responses.

See `DRF serializer documentation  <http://www.django-rest-framework.org/api-guide/serializers/>`_
Used by the View classes api/views.py to serialize API responses as JSON or HTML.
See DEFAULT_RENDERER_CLASSES setting in core.settings.contrib for the enabled renderers.
"""
# -*- coding: utf-8 -*-
import logging

from django.db import transaction
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

# Get an instance of a logger
LOG = logging.getLogger(__name__)

class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField()

class ExportTaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = ExportTask
        fields = ('uid', 'name', 'status', 'started_at', 'finished_at', 
                  'duration', 'filesize_bytes','filenames', 'download_url')

class ExportRunSerializer(serializers.ModelSerializer):
    tasks = ExportTaskSerializer(many=True,read_only=True)

    class Meta:
        model = ExportRun
        lookup_field = 'uid'
        fields = ('uid', 'started_at', 'finished_at', 'duration', 
                  'user', 'status', 'tasks')

class JobSerializer(serializers.ModelSerializer):
    runs = ExportRunSerializer(many=True,read_only=True)

    class Meta:
        model = Job
        fields = ('id', 'uid', 'user', 'name','runs',
                  'description', 'event', 'export_formats', 'published',
                  'the_geom', 'feature_selection','buffer_aoi')

class ListJobSerializer(serializers.ModelSerializer):
    """
    Return a sub-set of Job model attributes.

    Provides a stripped down set of export attributes.
    Used to display the list of exports in the export browser.
    """
    class Meta:
        model = Job
        fields = ('id', 'uid', 'user', 'name','description', 'event', 'export_formats', 'published')


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
