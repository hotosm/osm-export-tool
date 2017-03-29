# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import uuid

from django.contrib.auth.models import Group, User
from django.contrib.gis.db import models
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.postgres.fields import ArrayField
from django.db.models.fields import CharField
from django.db.models.signals import post_delete, post_save
from django.dispatch.dispatcher import receiver
from django.utils import timezone

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
    the_geom = models.PolygonField(verbose_name='Extent for export', srid=4326, default='')
    the_geom_webmercator = models.PolygonField(verbose_name='Mercator extent for export', srid=3857, default='')
    the_geog = models.PolygonField(verbose_name='Geographic extent for export', geography=True, default='')
    objects = models.GeoManager()

    class Meta:  # pragma: no cover
        managed = True
        db_table = 'jobs'

    def save(self, *args, **kwargs):
        self.the_geog = GEOSGeometry(self.the_geom)
        self.the_geom_webmercator = self.the_geom.transform(ct=3857, clone=True)
        super(Job, self).save(*args, **kwargs)

    def __str__(self):
        return '{0}'.format(self.name)

    @property
    def overpass_extents(self, ):
        """
        Return the export extents in order required by Overpass API.
        """
        extents = GEOSGeometry(self.the_geom).extent  # (w,s,e,n)
        # overpass needs extents in order (s,w,n,e)
        overpass_extents = '{0},{1},{2},{3}'.format(str(extents[1]), str(extents[0]),
                                                    str(extents[3]), str(extents[2]))
        return overpass_extents

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


class ExportProfile(models.Model):
    """
    Model to hold Group export profile.
    """
    name = models.CharField(max_length=100, blank=False, default='')
    group = models.OneToOneField(Group, related_name='export_profile')
    max_extent = models.IntegerField()

    class Meta:  # pragma: no cover
        managed = True
        db_table = 'export_profiles'

    def __str__(self):
        return '{0}'.format(self.name)


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


@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    """
    This method is executed whenever a User object is created.

    Adds the new user to DefaultExportExtentGroup.
    """
    if created:
        instance.groups.add(Group.objects.get(name='DefaultExportExtentGroup'))
