# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from ..models import Region
from django.contrib.gis.geos import GEOSGeometry

class Migration(migrations.Migration):
    
    def insert_regions(apps, schema_editor):
        Region = apps.get_model('jobs', 'Region')
        
        ds = DataSource(os.path.dirname(os.path.realpath(__file__)) + '/africa.geojson')
        geom = layer.get_geoms(geos=True)[0]
        the_geom = GEOSGeometry(geom.wkt, srid=4326)
        the_geog = GEOSGeometry(geom.wkt)
        the_geom_webmercator = the_geom.transform(ct=3857, clone=True)
        region = Region.objects.create(name="Africa", description="African export region",
                        the_geom=the_geom, the_geog=the_geog, the_geom_webmercator=the_geom_webmercator
        )
        
        ds = DataSource(os.path.dirname(os.path.realpath(__file__)) + '/burma.geojson')
        geom = layer.get_geoms(geos=True)[0]
        the_geom = GEOSGeometry(geom.wkt, srid=4326)
        the_geog = GEOSGeometry(geom.wkt)
        the_geom_webmercator = the_geom.transform(ct=3857, clone=True)
        region = Region.objects.create(name="Burma", description="Burmese export region",
                        the_geom=the_geom, the_geog=the_geog, the_geom_webmercator=the_geom_webmercator
        )
        
        ds = DataSource(os.path.dirname(os.path.realpath(__file__)) + '/central_asia.geojson')
        geom = layer.get_geoms(geos=True)[0]
        the_geom = GEOSGeometry(geom.wkt, srid=4326)
        the_geog = GEOSGeometry(geom.wkt)
        the_geom_webmercator = the_geom.transform(ct=3857, clone=True)
        region = Region.objects.create(name="Central Asia/Middle East", description="Central Asia/Middle East export region",
                        the_geom=the_geom, the_geog=the_geog, the_geom_webmercator=the_geom_webmercator
        )
        
        ds = DataSource(os.path.dirname(os.path.realpath(__file__)) + '/indonesia.geojson')
        geom = layer.get_geoms(geos=True)[0]
        the_geom = GEOSGeometry(geom.wkt, srid=4326)
        the_geog = GEOSGeometry(geom.wkt)
        the_geom_webmercator = the_geom.transform(ct=3857, clone=True)
        region = Region.objects.create(name="Indonesia, Sri Lanka, and Bangladesh", description="Indonesia, Sri Lanka, and Bangladesh export region",
                        the_geom=the_geom, the_geog=the_geog, the_geom_webmercator=the_geom_webmercator
        )
        
        ds = DataSource(os.path.dirname(os.path.realpath(__file__)) + '/philippines.geojson')
        geom = layer.get_geoms(geos=True)[0]
        the_geom = GEOSGeometry(geom.wkt, srid=4326)
        the_geog = GEOSGeometry(geom.wkt)
        the_geom_webmercator = the_geom.transform(ct=3857, clone=True)
        region = Region.objects.create(name="Philippines", description="Philippines export region",
                        the_geom=the_geom, the_geog=the_geog, the_geom_webmercator=the_geom_webmercator
        )
        
        ds = DataSource(os.path.dirname(os.path.realpath(__file__)) + '/south_america.geojson')
        geom = layer.get_geoms(geos=True)[0]
        the_geom = GEOSGeometry(geom.wkt, srid=4326)
        the_geog = GEOSGeometry(geom.wkt)
        the_geom_webmercator = the_geom.transform(ct=3857, clone=True)
        region = Region.objects.create(name="South and Central America", description="South and Central America export region",
                        the_geom=the_geom, the_geog=the_geog, the_geom_webmercator=the_geom_webmercator
        )
        
        

    dependencies = [
        ('jobs', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(insert_regions),
    ]
