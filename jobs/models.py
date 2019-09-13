# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import calendar
from datetime import timedelta
import logging
import json
import uuid
import re

from django.conf import settings
from django.contrib.auth.models import User, Group
from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField
from django.db.models.fields import CharField
from django.utils import timezone
from django.core.exceptions import ValidationError
import mercantile

from hdx_exports.hdx_export_set import HDXExportSet
from feature_selection.feature_selection import FeatureSelection
from utils.aoi_utils import simplify_geom, get_geodesic_area, check_extent, force2d
from django.contrib import admin

LOG = logging.getLogger(__name__)
MAX_TILE_COUNT = 10000

Group.add_to_class('is_partner', models.BooleanField(null=False, default=False))

def validate_export_formats(value):
    if not value:
        raise ValidationError(
            "Must choose at least one export format."
        )

    for format_name in value:
        if format_name not in ['shp','geopackage','garmin_img','kml','mwm','osmand_obf','osm_pbf','osm_xml','bundle','mbtiles','full_pbf']:
            raise ValidationError(
                "Bad format name: %(format_name)s",
                params={'format_name': format_name},
            )

def validate_feature_selection(value):
    f = FeatureSelection(value)
    if not f.valid:
        raise ValidationError(f.errors)

def validate_aoi(aoi):
    result = check_extent(aoi,settings.OVERPASS_API_URL)
    if not result.valid:
        raise ValidationError(result.message,params=result.params)
    
def validate_mbtiles(job):
    if "mbtiles" in job["export_formats"]:
        if job.get("mbtiles_source") is None:
            raise ValidationError("A source is required when generating an MBTiles archive.")

        if job.get("mbtiles_maxzoom") is None or job.get("mbtiles_minzoom") is None:
            raise ValidationError("A zoom range must be provided when generating an MBTiles archive.")

        bounds = job["the_geom"].extent
        tile_count = 0

        for z in xrange(int(job["mbtiles_minzoom"]), int(job["mbtiles_maxzoom"])):
            sw = mercantile.tile(*bounds[0:2], zoom=z)
            ne = mercantile.tile(*bounds[2:4], zoom=z)

            width = 1 + ne[0] - sw[0]
            height = 1 + sw[1] - ne[1]

            tile_count += width * height

        if tile_count > MAX_TILE_COUNT:
            raise ValidationError(
                "%(tile_count)s tiles would be rendered; please reduce the zoom range, the size of your AOI, or split the export into pieces covering specific areas in order to render fewer than %(max_tile_count)s in each.",
                params={'tile_count': tile_count, 'max_tile_count': MAX_TILE_COUNT},
            )

class Job(models.Model):
    """ 
    Database model for an 'Export'.
    Immutable, except in the case of HDX Export Regions.
    """
    id = models.AutoField(primary_key=True, editable=False)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False, db_index=True)
    user = models.ForeignKey(User, related_name='owner')
    name = models.CharField(max_length=100, db_index=True, blank=False)
    description = models.CharField(max_length=1000, db_index=True, default='', blank=True)
    event = models.CharField(max_length=100, db_index=True, default='', blank=True)
    export_formats = ArrayField(models.CharField(max_length=10),validators=[validate_export_formats],blank=False)
    published = models.BooleanField(default=False, db_index=True)
    the_geom = models.GeometryField(verbose_name='Uploaded geometry', srid=4326, blank=False)
    simplified_geom = models.GeometryField(verbose_name='Simplified geometry', srid=4326, blank=True,null=True)
    objects = models.GeoManager()
    feature_selection = models.TextField(blank=False,validators=[validate_feature_selection])
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now, editable=False)
    mbtiles_maxzoom = models.IntegerField(null=True,blank=True)
    mbtiles_minzoom = models.IntegerField(null=True,blank=True)
    mbtiles_source = models.TextField(null=True,blank=True)

    # flags
    buffer_aoi = models.BooleanField(default=False)
    unlimited_extent = models.BooleanField(default=False)
    hidden = models.BooleanField(default=False) # hidden from the list page
    expire_old_runs = models.BooleanField(default=True)
    per_theme = models.BooleanField(default=False)

    class Meta:  # pragma: no cover
        managed = True
        db_table = 'jobs'

    @property
    def osma_link(self):
        bounds = self.the_geom.extent
        return "http://osm-analytics.org/#/show/bbox:{0},{1},{2},{3}/buildings/recency".format(*bounds)

    @property
    def feature_selection_object(self):
        """
        a valid FeatureSelection object based off the feature_selection text column.
        """
        return FeatureSelection(self.feature_selection)

    @property
    def area(self):
        return get_geodesic_area(self.the_geom)

    def save(self, *args, **kwargs):
        self.the_geom = force2d(self.the_geom)
        self.simplified_geom = simplify_geom(self.the_geom,force_buffer=self.buffer_aoi)
        super(Job, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.uid)


class SavedFeatureSelection(models.Model):
    """ Mutable database record for a saved YAML configuration."""
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now, editable=False)
    user = models.ForeignKey(User)
    name = models.CharField(max_length=100,db_index=True,blank=False)
    description = models.CharField(max_length=1000, db_index=True, default='', blank=True)
    yaml = models.TextField(blank=False,validators=[validate_feature_selection])
    public = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False, db_index=True)
    pinned = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name)

PERIOD_CHOICES = (
    ('6hrs', 'Every 6 hours'),
    ('daily', 'Every day'),
    ('weekly', 'Every Sunday'),
    ('monthly', 'The 1st of every month'),
    ('disabled', 'Disabled'),
)
HOUR_CHOICES = zip(range(0, 24), range(0, 24))

class PartnerExportRegion(models.Model):
    schedule_period = models.CharField(
        blank=False, max_length=10, default="disabled", choices=PERIOD_CHOICES)
    schedule_hour = models.IntegerField(
        blank=False, choices=HOUR_CHOICES, default=0)
    job = models.ForeignKey(Job, null=True)
    # the owning group, which determines access control.
    group = models.ForeignKey(Group)
    deleted = models.BooleanField(default=False)

    @property
    def last_run(self): # noqa
        if self.job.runs.count() > 0:
            return self.job.runs.all()[self.job.runs.count() - 1].finished_at

    @property
    def last_size(self):
        if self.job.runs.count() > 0:
            return self.job.runs.all()[self.job.runs.count() - 1].size

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
    def job_uid(self):
        return self.job.uid

    @property
    def feature_selection(self): # noqa
        return self.job.feature_selection

    @property
    def export_formats(self): # noqa
        return self.job.export_formats

    @property
    def name(self): # noqa
        return self.job.name

    @property
    def the_geom(self):
        return self.job.the_geom

    @property
    def simplified_geom(self): # noqa
        return self.job.simplified_geom

    @property
    def group_name(self):
        return self.group.name

class HDXExportRegion(models.Model): # noqa
    """ Mutable database table for hdx - additional attributes on a Job."""
    schedule_period = models.CharField(
        blank=False, max_length=10, default="disabled", choices=PERIOD_CHOICES)
    schedule_hour = models.IntegerField(
        blank=False, choices=HOUR_CHOICES, default=0)
    deleted = models.BooleanField(default=False)
    # a job should really be required, but that interferes with DRF validation lifecycle.
    job = models.ForeignKey(Job, null=True, related_name='hdx_export_region_set')
    is_private = models.BooleanField(default=False)
    locations = ArrayField(
        models.CharField(blank=False, max_length=32), null=True)
    license = models.CharField(max_length=32, null=True,blank=True)
    subnational = models.BooleanField(default=True)
    extra_notes = models.TextField(null=True,blank=True)

    class Meta: # noqa
        db_table = 'hdx_export_regions'

    def __str__(self):
        return self.name + " (prefix: " + self.dataset_prefix + ")"

    def clean(self):
        if self.job and not re.match(r'^[a-z0-9-_]+$',self.job.name):
            raise ValidationError({'dataset_prefix':"Invalid dataset_prefix: {0}".format(self.job.name)})

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
    def last_size(self):
        if self.job.runs.count() > 0:
            return self.job.runs.all()[self.job.runs.count() - 1].size

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
    def the_geom(self):
        return self.job.the_geom

    @property
    def simplified_geom(self): # noqa
        return self.job.simplified_geom

    @property
    def feature_selection(self): # noqa
        return self.job.feature_selection

    @property
    def export_formats(self): # noqa
        return self.job.export_formats

    @property
    def datasets(self): # noqa
        return self.hdx_dataset.dataset_links(settings.HDX_URL_PREFIX)

    @property
    def job_uid(self):
        return self.job.uid

    @property
    def hdx_dataset(self): # noqa
        """
        Initialize an HDXExportSet corresponding to this Model.
        """
#       # TODO make distinction between GOESGeom/GeoJSON better
        return HDXExportSet(
            data_update_frequency=self.update_frequency,
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




