"""
    Harness for running thematic transformations against a spatialite db.

    From the project directory run:
    ./manage.py runscript thematic_test --settings=hot_exports.settings -v2
    Depends on django-extensions.
"""

import logging
import os
import shutil
import sqlite3
from string import Template

from oet2.jobs.models import Job

logger = logging.getLogger(__name__)

thematic_spec = {
    'amenities_all_points': {'type': 'point', 'key': 'amenity', 'table': 'planet_osm_point', 'select_clause': 'amenity is not null'},
    'amenities_all_polygons': {'type': 'polygon', 'key': 'amenity', 'table': 'planet_osm_polygon', 'select_clause': 'amenity is not null'},
    'health_schools_points': {'type': 'point', 'key': 'amenity', 'table': 'planet_osm_point', 'select_clause': 'amenity="clinic" OR amenity="hospital" OR amenity="school" OR amenity="pharmacy"'},
    'health_schools_polygons': {'key': 'amenity', 'table': 'planet_osm_polygon', 'select_clause': 'amenity="clinic" OR amenity="hospital" OR amenity="school" OR amenity="pharmacy"'},
    'airports_all_points': {'key': 'aeroway', 'table': 'planet_osm_point', 'select_clause': 'aeroway is not null'},
    'airports_all_polygons': {'key': 'aeroway', 'table': 'planet_osm_polygon', 'select_clause': 'aeroway is not null'},
    'villages_points': {'key': 'place', 'table': 'planet_osm_point', 'select_clause': 'place is not null'},
    'buildings_polygons': {'key': 'building', 'table': 'planet_osm_polygon', 'select_clause': 'building is not null'},
    'natural_polygons': {'key': 'natural', 'table': 'planet_osm_polygon', 'select_clause': 'natural is not null'},
    'natural_lines': {'key': 'natural', 'table': 'planet_osm_line', 'select_clause': 'natural is not null'},
    'landuse_other_polygons': {'key': 'landuse', 'table': 'planet_osm_polygon', 'select_clause': 'landuse is not null AND landuse!="residential"'},
    'landuse_residential_polygons': {'key': 'landuse', 'table': 'planet_osm_polygon', 'select_clause': 'landuse is not null AND landuse="residential"'},
    'roads_paths_lines': {'key': 'highway', 'table': 'planet_osm_line', 'select_clause': 'highway is not null'},
    'waterways_lines': {'key': 'waterway', 'table': 'planet_osm_line', 'select_clause': 'waterway is not null'},
    'towers_antennas_points': {'key': 'man_made', 'table': 'planet_osm_point', 'select_clause': 'man_made="antenna" OR man_made="mast" OR man_made="tower"'},
    'harbours_points': {'key': 'harbour', 'table': 'planet_osm_point', 'select_clause': 'harbour is not null'},
    'grassy_fields_polygons': {'key': 'leisure', 'table': 'planet_osm_polygon', 'select_clause': 'leisure="pitch" OR leisure="common" OR leisure="golf_course"'},
}


def run(*script_args):

    sqlite = '/home/ubuntu/export_downloads/5c095634-1591-4f31-aa75-b6a7952b29e9/query.sqlite'
    thematic = '/home/ubuntu/export_downloads/5c095634-1591-4f31-aa75-b6a7952b29e9/thematic.sqlite'

    # get the job tags
    job = Job.objects.get(uid='0a835fe4-1fbc-43ad-ab37-940fab415085')
    tags = job.categorised_tags

    # create the thematic sqlite file (a copy of the original)
    thematic_sqlite = shutil.copy(sqlite, thematic)
    assert os.path.exists(thematic), 'Thematic sqlite file not found.'

    # setup sqlite connection
    conn = sqlite3.connect(thematic)
    # load spatialite extension
    conn.enable_load_extension(True)
    cmd = "SELECT load_extension('libspatialite')"
    cur = conn.cursor()
    cur.execute(cmd)
    geom_types = {'points': 'POINT', 'lines': 'LINESTRING', 'polygons': 'MULTIPOLYGON'}
    # create and execute thematic sql statements
    sql_tmpl = Template('CREATE TABLE $tablename AS SELECT osm_id, $osm_way_id $columns, Geometry FROM $planet_table WHERE $select_clause')
    recover_geom_tmpl = Template("SELECT RecoverGeometryColumn($tablename, 'GEOMETRY', 4326, $geom_type, 'XY')")
    for layer, spec in thematic_spec.iteritems():
        layer_type = layer.split('_')[-1]
        isPoly = layer_type == 'polygons'
        osm_way_id = ''
        # check if the thematic tag is in the jobs tags, if not skip this thematic layer
        if not spec['key'] in tags[layer_type]:
            continue
        if isPoly:
            osm_way_id = 'osm_way_id,'
        params = {'tablename': layer, 'osm_way_id': osm_way_id,
                  'columns': ', '.join(tags[layer_type]),
                  'planet_table': spec['table'], 'select_clause': spec['select_clause']}
        sql = sql_tmpl.safe_substitute(params)
        print sql
        cur.execute(sql)
        geom_type = geom_types[layer_type]

        recover_geom_sql = recover_geom_tmpl.safe_substitute({'tablename': "'" + layer + "'", 'geom_type': "'" + geom_type + "'"})
        print recover_geom_sql
        conn.commit()
        cur.execute(recover_geom_sql)
        cur.execute("SELECT CreateSpatialIndex({0}, 'GEOMETRY')".format("'" + layer + "'"))
        conn.commit()

    # remove existing geometry columns
    cur.execute("SELECT DiscardGeometryColumn('planet_osm_point','Geometry')")
    cur.execute("SELECT DiscardGeometryColumn('planet_osm_line','Geometry')")
    cur.execute("SELECT DiscardGeometryColumn('planet_osm_polygon','Geometry')")
    conn.commit()

    # drop existing spatial indexes
    cur.execute('DROP TABLE idx_planet_osm_point_GEOMETRY')
    cur.execute('DROP TABLE idx_planet_osm_line_GEOMETRY')
    cur.execute('DROP TABLE idx_planet_osm_polygon_GEOMETRY')
    conn.commit()

    # drop default schema tables
    cur.execute('DROP TABLE planet_osm_point')
    cur.execute('DROP TABLE planet_osm_line')
    cur.execute('DROP TABLE planet_osm_polygon')
    conn.commit()
    cur.close()
