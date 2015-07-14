from __future__ import unicode_literals
import uuid
import logging
#from django.db import models
from django.contrib.gis.db import models
from django.contrib.postgres.fields import HStoreField
from django.contrib.gis.geos import GEOSGeometry
from django.utils import timezone
from django.contrib.auth.models import User, Group
from django.db.models.fields import CharField
from django.db.models.signals import post_delete
from django.dispatch.dispatcher import receiver

logger = logging.getLogger(__name__) 

# construct the upload path for export config files..
def get_upload_path(instance, filename):
    configtype = instance.config_type.lower()
    # sanitize the filename here..
    path = 'export/config/{0}/{1}'.format(configtype, instance.filename)
    logger.debug('Saving export config to /media/{0}'.format(path))
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
    
    class Meta:
        abstract = True
        

class ExportConfig(TimeStampedModelMixin):
    """
    Model for export configuration.
    """
    PRESET = 'PRESET'
    TRANSLATION = 'TRANSLATION'
    TRANSFORM = 'TRANSFORM'
    CONFIG_TYPES = (
        (PRESET, 'Preset'),
        (TRANSLATION, 'Translation'),
        (TRANSFORM, 'Transform')
    )
    id = models.AutoField(primary_key=True, editable=False)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, default='', db_index=True)
    user = models.ForeignKey(User, related_name='user')
    config_type = models.CharField(max_length=11, choices=CONFIG_TYPES, default=PRESET)
    filename = models.CharField(max_length=255)
    upload = models.FileField(max_length=255, upload_to=get_upload_path)
    content_type = models.CharField(max_length=30, editable=False)
    visible = models.BooleanField(default=True)
    
    class Meta:
        managed = True
        db_table = 'export_configurations'


class ExportFormat(TimeStampedModelMixin):
    """Model for a ExportFormat"""
    id = models.AutoField(primary_key=True, editable=False)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False, db_index=True)
    name = models.CharField(max_length=100)
    slug = LowerCaseCharField(max_length=7, unique=True, default='')    
    description = models.CharField(max_length=255)
    cmd = models.TextField(max_length=1000)
    objects = models.Manager()
    
    class Meta:
        managed = True
        db_table = 'export_formats'
        
    def __str__(self):
        return '{0}'.format(self.name)
    
    def __unicode__(self, ):
        return '{0}'.format(self.slug)
    

class Region(TimeStampedModelMixin):
    """
    Model for a HOT Export Region.
    """
    id = models.AutoField(primary_key=True, editable=False)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, db_index=True)
    description = models.CharField(max_length=1000, blank=True)
    the_geom = models.PolygonField(verbose_name='HOT Export Region', srid=4326, default='')
    the_geom_webmercator = models.PolygonField(verbose_name='Mercator extent for export region', srid=3857, default='')
    the_geog = models.PolygonField(verbose_name='Geographic extent for export region', geography=True, default='') 
    objects = models.GeoManager()
    
    class Meta:
        managed = True
        db_table = 'regions'
    
    def __str__(self):
        return '{0}'.format(self.name)
    
    
class Tag(models.Model):
    """
    Model to represent export tags.
    """
    id = models.AutoField(primary_key=True, editable=False)
    name = models.CharField(max_length=50)
    geom_types = HStoreField()
    
    class Meta:
        managed = True
        db_table = 'tags'
    
    def __str__(self):
        return '{0}: {1}'.format(self.name, self.geom_types)
    

class Job(TimeStampedModelMixin):
    """
    Model for a Job.
    """
    id = models.AutoField(primary_key=True, editable=False)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False, db_index=True)
    user = models.ForeignKey(User, related_name='owner')
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    event = models.CharField(max_length=100, db_index=True, default='')
    region = models.ForeignKey(Region, null=True)
    formats = models.ManyToManyField(ExportFormat, related_name='formats')
    configs = models.ManyToManyField(ExportConfig, related_name='configs')
    tags = models.ManyToManyField(Tag, related_name='tags')
    the_geom = models.PolygonField(verbose_name='Extent for export', srid=4326, default='')
    the_geom_webmercator = models.PolygonField(verbose_name='Mercator extent for export', srid=3857, default='')
    the_geog = models.PolygonField(verbose_name='Geographic extent for export', geography=True, default='')
    objects = models.GeoManager()
    
    class Meta:
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
        extents = GEOSGeometry(self.the_geom).extent # (w,s,e,n)
        # overpass needs extents in order (s,w,n,e)
        overpass_extents = '{0},{1},{2},{3}'.format(str(extents[1]), str(extents[0]), str(extents[3]), str(extents[2]))
        return overpass_extents
    
    @property
    def tag_dict(self,):
        tag_dict = {}
        for tag in self.tags.all():
            tag_dict[tag.name] = tag.geom_types
        return tag_dict
    
    @property
    def categorised_tags(self,):
        points = []
        lines = []
        polygons = []
        for tag in self.tag_dict:
            for geom in self.tag_dict[tag].keys():
                if geom == 'point':
                    points.append(tag)
                if geom == 'line':
                    lines.append(tag)
                if geom == 'polygon':
                    polygons.append(tag)
        return {'points': sorted(points), 'lines': sorted(lines), 'polygons': sorted(polygons)}
    
    

class RegionMask(models.Model):
    
    id = models.IntegerField(primary_key=True)
    the_geom = models.MultiPolygonField(verbose_name='Mask for export regions', srid=4326)
    
    class Meta:
        managed = False
        db_table = 'region_mask'

"""
Delete the associated file when the export config is deleted.
"""
@receiver(post_delete, sender=ExportConfig)
def exportconfig_delete_upload(sender, instance, **kwargs):
    instance.upload.delete(False)
    





