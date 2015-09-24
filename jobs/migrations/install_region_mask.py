# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
from django.db import models, migrations

class Migration(migrations.Migration):
    
    
    dependencies = [
        ('jobs', '0012_auto_20150908_1226'),
    ]
    
    
    operations = [
        migrations.RunSQL('DROP VIEW IF EXISTS exports.region_mask;'),
        migrations.RunSQL("""CREATE OR REPLACE VIEW exports.region_mask AS
                          select 1 as id,
                          st_multi(st_symdifference(st_polyfromtext('POLYGON((-180 90, -180 -90, 180 -90, 180 90, -180 90))', 4326), st_union(the_geom)))
                          AS the_geom
                          FROM exports.regions;"""),
        migrations.RunSQL("ALTER TABLE exports.region_mask OWNER TO hot;")
    ]
