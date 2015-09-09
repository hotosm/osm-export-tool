from __future__ import unicode_literals
import uuid
import logging
import pdb
#from django.db import models
from django.contrib.gis.db import models
from django.contrib.postgres.fields import HStoreField
from django.contrib.postgres.fields import ArrayField
from django.contrib.gis.geos import GEOSGeometry
from django.utils import timezone
from django.contrib.auth.models import User, Group
from django.db.models.fields import CharField
from django.db.models.signals import post_delete, post_save
from django.dispatch.dispatcher import receiver

logger = logging.getLogger(__name__) 

# construct the upload path for export config files..
def get_upload_path(instance, filename):
    #pdb.set_trace()
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
    
    class Meta: # pragma: no cover
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
    published = models.BooleanField(default=False)
    
    class Meta: # pragma: no cover
        managed = True
        db_table = 'export_configurations'


class ExportFormat(TimeStampedModelMixin):
    """Model for a ExportFormat"""
    id = models.AutoField(primary_key=True, editable=False)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False, db_index=True)
    name = models.CharField(max_length=100)
    slug = LowerCaseCharField(max_length=10, unique=True, default='')    
    description = models.CharField(max_length=255)
    cmd = models.TextField(max_length=1000)
    objects = models.Manager()
    
    class Meta: # pragma: no cover
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
    
    class Meta: # pragma: no cover
        managed = True
        db_table = 'regions'
    
    def __str__(self):
        return '{0}'.format(self.name)


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
    region = models.ForeignKey(Region, null=True)
    formats = models.ManyToManyField(ExportFormat, related_name='formats')
    configs = models.ManyToManyField(ExportConfig, related_name='configs')
    published = models.BooleanField(default=False, db_index=True) # publish export
    feature_save = models.BooleanField(default=False, db_index=True) # save feature selections
    feature_pub = models.BooleanField(default=False, db_index=True) # publish feature selections
    the_geom = models.PolygonField(verbose_name='Extent for export', srid=4326, default='')
    the_geom_webmercator = models.PolygonField(verbose_name='Mercator extent for export', srid=3857, default='')
    the_geog = models.PolygonField(verbose_name='Geographic extent for export', geography=True, default='')
    objects = models.GeoManager()
    
    class Meta: # pragma: no cover
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
        overpass_extents = '{0},{1},{2},{3}'.format(str(extents[1]), str(extents[0]),
                                                    str(extents[3]), str(extents[2]))
        return overpass_extents
    
    @property
    def tag_dict(self,):
        # get the unique keys from the tags for this export
        uniq_keys = list(self.tags.values('key').distinct('key'))
        tag_dict = {} # mapping of tags to geom_types
        for entry in uniq_keys:
            key = entry['key']
            tag_dict['key'] = key
            geom_types = list(self.tags.filter(key=key).values('geom_types'))
            geom_type_list = []
            for geom_type in geom_types:
                geom_list = geom_type['geom_types']
                geom_type_list.extend([i for i in geom_list])
            tag_dict[key] = list(set(geom_type_list)) # get unique values for geomtypes
        return tag_dict
    
    @property
    def categorised_tags(self,):
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
    key = models.CharField(max_length=30, blank=False, default='', db_index=True)
    value = models.CharField(max_length=30, blank=False, default='', db_index=True)
    job = models.ForeignKey(Job, related_name='tags')
    data_model = models.CharField(max_length=10, blank=False, default='', db_index=True)
    geom_types = ArrayField(models.CharField(max_length=10, blank=True, default=''), default=[])
    groups = ArrayField(models.CharField(max_length=100, blank=True, default=''), default=[])
    
    class Meta: # pragma: no cover
        managed = True
        db_table = 'tags'
    
    def __str__(self): # pragma: no cover
        return '{0}:{1}'.format(self.key, self.value)
    

class RegionMask(models.Model):
    
    id = models.IntegerField(primary_key=True)
    the_geom = models.MultiPolygonField(verbose_name='Mask for export regions', srid=4326)
    
    class Meta: # pragma: no cover
        managed = False
        db_table = 'region_mask'


class ExportProfile(models.Model):
    name = models.CharField(max_length=100, blank=False, default='')
    group = models.OneToOneField(Group, related_name='export_profile')
    max_extent = models.IntegerField()
    
    class Meta: # pragma: no cover
        managed = True
        db_table = 'export_profiles'
    
    def __str__(self):
        return '{0}'.format(self.name)



"""
Delete the associated file when the export config is deleted.
"""
@receiver(post_delete, sender=ExportConfig)
def exportconfig_delete_upload(sender, instance, **kwargs):
    instance.upload.delete(False)
    

"""
Add each newly registered user to the DefaultExportExtentGroup
"""
@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    """
    This method is executed whenever an user object is saved                                                                                     
    """
    if created:
        instance.groups.add(Group.objects.get(name='DefaultExportExtentGroup'))





