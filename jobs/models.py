# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import calendar
from datetime import timedelta
import logging
import json
import uuid
import math
import re

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.postgres.fields import ArrayField
from django.db.models.fields import CharField
from django.utils import timezone
from django.core.exceptions import ValidationError

from hdx_exports.hdx_export_set import HDXExportSet
from feature_selection.feature_selection import FeatureSelection
from utils import FORMAT_NAMES

LOG = logging.getLogger(__name__)

def get_geodesic_area(geom):
    """
    Uses the algorithm to calculate geodesic area of a polygon from OpenLayers 2.
    See http://bit.ly/1Mite1X.

    Args:
        geom (GEOSGeometry): the export extent as a GEOSGeometry.

    Returns
        area (float): the geodesic area of the provided geometry.
    """
    area = 0.0
    coords = geom.coords[0]
    length = len(coords)
    if length > 2:
        for x in range(length - 1):
            p1 = coords[x]
            p2 = coords[x+1]
            area += math.radians(p2[0] - p1[0]) * (2 + math.sin(math.radians(p1[1]))
                                                   + math.sin(math.radians(p2[1])))
        area = area * 6378137 * 6378137 / 2.0
    return area

def validate_aoi(aoi):
    area = get_geodesic_area(aoi)
    if area > 2500000:
        raise ValidationError(
            "Geometry too large: %(area)s km",
            params={'area': area},
        )

def validate_export_formats(value):
    if not value:
        raise ValidationError(
            "Must choose at least one export format."
        )

    for format_name in value:
        if format_name not in FORMAT_NAMES:
            raise ValidationError(
                "Bad format name: %(format_name)s",
                params={'format_name': format_name},
            )

def validate_feature_selection(value):
    f = FeatureSelection(value)
    if not f.valid:
        raise ValidationError(f.errors)

class Job(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False, db_index=True)
    user = models.ForeignKey(User, related_name='owner')
    name = models.CharField(max_length=100, db_index=True, blank=False)
    description = models.CharField(max_length=1000, db_index=True, default='', blank=True)
    event = models.CharField(max_length=100, db_index=True, default='', blank=True)
    export_formats = ArrayField(models.CharField(max_length=10),validators=[validate_export_formats],blank=False)
    published = models.BooleanField(default=False, db_index=True)
    the_geom = models.GeometryField(verbose_name='Extent for export', srid=4326, blank=False,validators=[validate_aoi])
    objects = models.GeoManager()
    feature_selection = models.TextField(blank=False,validators=[validate_feature_selection])
    buffer_aoi = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:  # pragma: no cover
        managed = True
        db_table = 'jobs'

    @property
    def feature_selection_object(self):
        """
        a valid FeatureSelection object based off the feature_selection text column.
        """
        return FeatureSelection(self.feature_selection)


class HDXExportRegion(models.Model): # noqa
    PERIOD_CHOICES = (
        ('6hrs', 'Every 6 hours'),
        ('daily', 'Every day'),
        ('weekly', 'Every Sunday'),
        ('monthly', 'The 1st of every month'),
        ('disabled', 'Disabled'),
    )
    HOUR_CHOICES = zip(xrange(0, 24), xrange(0, 24))
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
        return self.hdx_dataset.dataset_links(settings.HDX_URL_PREFIX)

    @property
    def job_uid(self):
        return self.job.uid

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
