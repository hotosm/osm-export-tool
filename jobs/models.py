# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import calendar
from datetime import timedelta
import logging
import json
import uuid

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.contrib.gis.db import models
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.postgres.fields import ArrayField
from django.db.models.fields import CharField
from django.db.models.signals import post_delete, post_save
from django.dispatch.dispatcher import receiver
from django.utils import timezone
from hdx.configuration import Configuration

from hdx_exports.hdx_export_set import HDXExportSet
from feature_selection.feature_selection import FeatureSelection
from utils import FORMAT_NAMES

LOG = logging.getLogger(__name__)

# construct the upload path for export config files..


def get_upload_path(instance, filename):
    """
    Construct the path to where the uploaded config file is to be stored.
    """
    configtype = instance.config_type.lower()
    # sanitize the filename here..
    path = 'export/config/{0}/{1}'.format(configtype, instance.filename)
    return path


class LowerCaseCharField(CharField):
    """
    Defines a charfield which automatically converts all inputs to
    lowercase and saves.
    """

    def pre_save(self, model_instance, add):
        """
        Converts the string to lowercase before saving.
        """
        current_value = getattr(model_instance, self.attname)
        setattr(model_instance, self.attname, current_value.lower())
        return getattr(model_instance, self.attname)


class TimeStampedModelMixin(models.Model):
    """
    Mixin for timestamped models.
    """
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:  # pragma: no cover
        abstract = True


class ExportConfig(TimeStampedModelMixin):
    """
    Model for export configuration.
    """
    PRESET = 'PRESET'
    CONFIG_TYPES = (
        (PRESET, 'Preset'),
    )
    id = models.AutoField(primary_key=True, editable=False)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, default='', db_index=True)
    user = models.ForeignKey(User, related_name='user')
    config_type = models.CharField(max_length=11, choices=CONFIG_TYPES, default=PRESET)
    filename = models.CharField(max_length=255)
    upload = models.FileField(max_length=255, upload_to=get_upload_path)
    content_type = models.CharField(max_length=30, editable=False)
    published = models.BooleanField(default=False)

    class Meta:  # pragma: no cover
        managed = True
        db_table = 'export_configurations'


class Job(TimeStampedModelMixin):
    """
    Model for a Job.
    """
    id = models.AutoField(primary_key=True, editable=False)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False, db_index=True)
    user = models.ForeignKey(User, related_name='owner')
    name = models.CharField(max_length=100, db_index=True)
    description = models.CharField(max_length=1000, db_index=True)
    event = models.CharField(max_length=100, db_index=True, default='', blank=True)
    export_formats = ArrayField(models.CharField(max_length=10), default=list)
    config = models.ForeignKey(ExportConfig, related_name = 'config',null=True)
    published = models.BooleanField(default=False, db_index=True)  # publish export
    feature_save = models.BooleanField(default=False, db_index=True)  # save feature selections
    feature_pub = models.BooleanField(default=False, db_index=True)  # publish feature selections
    the_geom = models.GeometryField(verbose_name='Extent for export', srid=4326, default='')
    objects = models.GeoManager()
    feature_selection = models.TextField(blank=True)
    buffer_aoi = models.BooleanField(default=False)

    class Meta:  # pragma: no cover
        managed = True
        db_table = 'jobs'

    def save(self, *args, **kwargs):
        super(Job, self).save(*args, **kwargs)

    def __str__(self):
        return '{0}'.format(self.name)


    @property
    def feature_selection_object(self):
        """
        a valid FeatureSelection object based off the feature_selection column.
        """
        fs = FeatureSelection(self.feature_selection)
        # assert fs.valid, 'Feature selection is invalid'
        return fs

    @property
    def tag_dict(self,):
        """
        Return the unique set of Tag keys from this export
        with their associated geometry types.

        Used by Job.categorised_tags (below) to categorize tags
        according to their geometry types.
        """
        # get the unique keys from the tags for this export
        uniq_keys = list(self.tags.values('key').distinct('key'))
        tag_dict = {}  # mapping of tags to geom_types
        for entry in uniq_keys:
            key = entry['key']
            tag_dict['key'] = key
            geom_types = list(self.tags.filter(key=key).values('geom_types'))
            geom_type_list = []
            for geom_type in geom_types:
                geom_list = geom_type['geom_types']
                geom_type_list.extend([i for i in geom_list])
            tag_dict[key] = list(set(geom_type_list))  # get unique values for geomtypes
        return tag_dict

    @property
    def filters(self,):
        """
        Return key=value pairs for each tag in this export.

        Used in utils.overpass.filter to filter the export.
        """
        filters = []
        for tag in self.tags.all():
            kv = '{0}={1}'.format(tag.key, tag.value)
            filters.append(kv)
        return filters

    @property
    def categorised_tags(self,):
        """
        Return tags mapped according to their geometry types.
        """
        points = []
        lines = []
        polygons = []
        for tag in self.tag_dict:
            for geom in self.tag_dict[tag]:
                if geom == 'point':
                    points.append(tag)
                if geom == 'line':
                    lines.append(tag)
                if geom == 'polygon':
                    polygons.append(tag)
        return {'points': sorted(points), 'lines': sorted(lines), 'polygons': sorted(polygons)}


class Tag(models.Model):
    """
    Model to hold Export tag selections.

    Holds the data model (osm | hdm | preset)
    and the geom_type mapping.
    """
    id = models.AutoField(primary_key=True, editable=False)
    name = models.CharField(max_length=100, blank=False, default='', db_index=True)
    key = models.CharField(max_length=50, blank=False, default='', db_index=True)
    value = models.CharField(max_length=50, blank=False, default='', db_index=True)
    job = models.ForeignKey(Job, related_name='tags')
    data_model = models.CharField(max_length=10, blank=False, default='', db_index=True)
    geom_types = ArrayField(models.CharField(max_length=10, blank=True, default=''), default=[])
    groups = ArrayField(models.CharField(max_length=100, blank=True, default=''), default=[])

    class Meta:  # pragma: no cover
        managed = True
        db_table = 'tags'

    def __str__(self):  # pragma: no cover
        return '{0}:{1}'.format(self.key, self.value)


class HDXExportRegion(models.Model): # noqa
    PERIOD_CHOICES = (
        ('6hrs', 'Every 6 hours'),
        ('daily', 'Every day'),
        ('weekly', 'Every Sunday'),
        ('monthly', 'The 1st of every month'),
        ('disabled', 'Disabled'),
    )
    HOUR_CHOICES = zip(xrange(0, 24), xrange(0, 24))
    EXPORT_FORMAT_CHOICES = map(
        lambda name: (name, FORMAT_NAMES[name].description), FORMAT_NAMES)
    schedule_period = models.CharField(
        blank=False, max_length=10, default="disabled", choices=PERIOD_CHOICES)
    schedule_hour = models.IntegerField(
        blank=False, choices=HOUR_CHOICES, default=0)
    deleted = models.BooleanField(default=False)
    job = models.ForeignKey(Job, null=True,
        related_name='hdx_export_region_set')
    is_private = models.BooleanField(default=False)
    locations = ArrayField(
        models.CharField(blank=False, max_length=32), null=True)
    license = models.CharField(max_length=32, null=True)
    subnational = models.BooleanField(default=True)
    extra_notes = models.TextField(null=True)

    class Meta: # noqa
        db_table = 'hdx_export_regions'

    @property
    def delta(self): # noqa
        if self.schedule_period == '6hrs':
            return timedelta(hours=6)

        if self.schedule_period == 'daily':
            return timedelta(days=1)

        if self.schedule_period == 'weekly':
            return timedelta(days=7)

        if self.schedule_period == 'monthly':
            return timedelta(days=31)

    @property
    def next_run(self): # noqa
        now = timezone.now().replace(minute=0, second=0, microsecond=0)

        if self.schedule_period == '6hrs':
            delta = 6 - (self.schedule_hour + now.hour % 6)

            return now + timedelta(hours=delta)

        now = now.replace(hour=self.schedule_hour)

        if self.schedule_period == 'daily':
            anchor = now

            if timezone.now() < anchor:
                return anchor

            return anchor + timedelta(days=1)

        if self.schedule_period == 'weekly':
            # adjust so the week starts on Sunday
            anchor = now - timedelta((now.weekday() + 1) % 7)

            if timezone.now() < anchor:
                return anchor

            return anchor + timedelta(days=7)

        if self.schedule_period == 'monthly':
            (_, num_days) = calendar.monthrange(now.year, now.month)
            anchor = now.replace(day=1)

            if timezone.now() < anchor:
                return anchor

            return anchor + timedelta(days=num_days)

    @property
    def last_run(self): # noqa
        if self.job.runs.count() > 0:
            return self.job.runs.all()[self.job.runs.count() - 1].finished_at

    @property
    def buffer_aoi(self): # noqa
        return self.job.buffer_aoi

    @property
    def name(self): # noqa
        return self.job.description

    @property
    def dataset_prefix(self): # noqa
        return self.job.name

    @property
    def the_geom(self): # noqa
        return json.loads(GEOSGeometry(self.job.the_geom).geojson)

    @property
    def feature_selection(self): # noqa
        return self.job.feature_selection

    @property
    def export_formats(self): # noqa
        return self.job.export_formats

    @property
    def datasets(self): # noqa
        return map(lambda x: {
            'name': '{}_{}'.format(self.dataset_prefix, x),
            'url': '{}dataset/{}_{}'.format(
                settings.HDX_URL_PREFIX, self.dataset_prefix, x),
        }, self.job.feature_selection_object.themes)

    @property
    def runs(self): # noqa
        return map(lambda run: {
            'elapsed_time': (run.finished_at or timezone.now()) - run.started_at,
            'run_at': run.started_at,
            'size': sum(map(
                lambda task: task.filesize_bytes or 0, run.tasks.all())),
            'status': run.status,
            'uid': run.uid,
        }, reversed(self.job.runs.all()))

    @property
    def hdx_dataset(self): # noqa
        """
        Initialize an HDXExportSet corresponding to this Model.
        """
#       # TODO make distinction between GOESGeom/GeoJSON better
        return HDXExportSet(
            data_update_frequency=self.update_frequency,
            dataset_date=timezone.now(),
            dataset_prefix=self.dataset_prefix,
            extent=self.job.the_geom,
            extra_notes=self.extra_notes,
            feature_selection=self.job.feature_selection_object,
            is_private=self.is_private,
            license=self.license,
            locations=self.locations,
            name=self.name,
            subnational=self.subnational,
        )

    @property
    def update_frequency(self):
        """Update frequencies in HDX form."""
        if self.schedule_period == '6hrs':
            return 1

        if self.schedule_period == 'daily':
            return 1

        if self.schedule_period == 'weekly':
            return 7

        if self.schedule_period == 'monthly':
            return 30

        return 0

    def sync_to_hdx(self): # noqa
        LOG.info("HDXExportRegion.sync_to_hdx called.")
        self.hdx_dataset.sync_datasets()

@receiver(post_delete, sender=ExportConfig)
def exportconfig_delete_upload(sender, instance, **kwargs):
    """
    Delete the associated file when the export config is deleted.
    """
    instance.upload.delete(False)
    # remove config from related jobs
    exports = Job.objects.filter(config__uid=instance.uid)
    for export in exports.all():
        export.config = None
        export.save()
