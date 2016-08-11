# -*- coding: utf-8 -*-
from __future__ import with_statement

import logging
import os
import shutil
import sqlite3
import subprocess
from string import Template

logger = logging.getLogger(__name__)


class ThematicSQliteToShp(object):
    """
    Thin wrapper around ogr2ogr to convert sqlite to shp using thematic layers.
    """

    def __init__(self, sqlite=None, shapefile=None, tags=None, job_name=None, zipped=True, debug=False):
        """
        Initialize the ThematicSQliteToShp utility.

        Args:
            sqlite: the sqlite file to convert
            shapefile: the path to the shapefile output
            tags: the selected tags for this export
            job_name: the name of the export job
            zipped: true if output is to be zipped, false otherwise
            debug: turn on/off debug logging output.
        """
        self.sqlite = sqlite
        self.tags = tags
        self.job_name = job_name
        if not os.path.exists(self.sqlite):
            raise IOError('Cannot find sqlite file for this task.')
        self.shapefile = shapefile
        self.zipped = zipped
        self.stage_dir = os.path.dirname(self.sqlite)
        if not self.shapefile:
            # create shp path from sqlite path.
            self.shapefile = self.stage_dir + '/' + self.job_name + '_thematic_shp'
        self.debug = debug
        self.cmd = Template("ogr2ogr -f 'ESRI Shapefile' $shp $sqlite -lco ENCODING=UTF-8")
        self.zip_cmd = Template("zip -j -r $zipfile $shp_dir")
        # create thematic sqlite file
        self.thematic_sqlite = self.stage_dir + '/' + self.job_name + '_thematic.sqlite'
        shutil.copy(self.sqlite, self.thematic_sqlite)
        assert os.path.exists(self.thematic_sqlite), 'Thematic sqlite file not found.'

        # think more about how to generate this more flexibly, eg. using admin / db / settings?
        self.thematic_spec = {
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

    def generate_thematic_schema(self,):
        """
        Generate the thematic schema.

        Iterates through the thematic_spec, checks the 'key' entry in the spec against
        the exports tags. Dynamically constructs sql statements to generate to
        generate the thematic layers based on the exports categoried_tags.
        """
        # setup sqlite connection
        conn = sqlite3.connect(self.thematic_sqlite)
        # load spatialite extension
        conn.enable_load_extension(True)
        cmd = "SELECT load_extension('mod_spatialite')"
        cur = conn.cursor()
        cur.execute(cmd)
        geom_types = {'points': 'POINT', 'lines': 'LINESTRING', 'polygons': 'MULTIPOLYGON'}
        # create and execute thematic sql statements
        sql_tmpl = Template('CREATE TABLE $tablename AS SELECT osm_id, $osm_way_id $columns, Geometry FROM $planet_table WHERE $select_clause')
        recover_geom_tmpl = Template("SELECT RecoverGeometryColumn($tablename, 'GEOMETRY', 4326, $geom_type, 'XY')")
        for layer, spec in self.thematic_spec.iteritems():
            layer_type = layer.split('_')[-1]
            isPoly = layer_type == 'polygons'
            osm_way_id = ''
            # check if the thematic tag is in the jobs tags, if not skip this thematic layer
            if not spec['key'] in self.tags[layer_type]:
                continue
            if isPoly:
                osm_way_id = 'osm_way_id,'

            """
            Construct the parameters for the thematic sql statement.
            Pull out the tags from self.tags according to their geometry type.
            See jobs.models.Job.categorised_tags property.
            """
            sql = ""
            params = {'tablename': layer, 'osm_way_id': osm_way_id,
                      'planet_table': spec['table'], 'select_clause': spec['select_clause']}

            # Ensure columns are available to migrate
            select_temp = Template('select * from $tablename LIMIT 1')
            sql = select_temp.safe_substitute({'tablename':spec['table']})
            try:
                col_cursor = cur.execute(sql)
            except Exception:
                logger.error("SQL Execute for: {}, has failed.".format(sql))
                raise
            col_names = [description[0] for description in col_cursor.description]
            temp_columns = []
            for column in [tag.replace(':', '_') for tag in self.tags[layer_type]]:
                if column in col_names:
                    temp_columns += [column]
            if temp_columns:
                params['columns'] = ', '.join(temp_columns)
            else:
                sql_tmpl = Template('CREATE TABLE $tablename AS SELECT osm_id, $osm_way_id, Geometry '
                                    'FROM $planet_table WHERE $select_clause')
            sql = sql_tmpl.safe_substitute(params)
            try:
                cur.execute(sql)
            except Exception:
                logger.error("SQL Execute for: {}, has failed.".format(sql))
                raise
            geom_type = geom_types[layer_type]
            recover_geom_sql = recover_geom_tmpl.safe_substitute({'tablename': "'" + layer + "'", 'geom_type': "'" + geom_type + "'"})
            conn.commit()
            try:
                cur.execute(recover_geom_sql)
                cur.execute("SELECT CreateSpatialIndex({0}, 'GEOMETRY')".format("'" + layer + "'"))
            except Exception:
                logger.error("SQL Execute for: {}, has failed.".format(sql))
                raise
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

    def convert(self, ):
        """
        Convert the thematic sqlite schema to shapefile.
        """
        convert_cmd = self.cmd.safe_substitute({'shp': self.shapefile, 'sqlite': self.thematic_sqlite})
        if(self.debug):
            print 'Running: %s' % convert_cmd
        proc = subprocess.Popen(convert_cmd, shell=True, executable='/bin/bash',
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = proc.communicate()
        returncode = proc.wait()
        if (returncode != 0):
            logger.error('%s', stderr)
            raise Exception, "ogr2ogr process failed with returncode {0}".format(returncode)
        if(self.debug):
            print 'ogr2ogr returned: %s' % returncode
        if self.zipped and returncode == 0:
            zipfile = self._zip_shape_dir()
            return zipfile
        else:
            return self.shapefile

    def _zip_shape_dir(self, ):
        """
        Zip the shapefile directory.
        """
        zipfile = self.shapefile + '.zip'
        if not os.listdir(self.shapefile):
            logger.warn("Attempted to zip an empty directory.")
            logger.warn("This is likely caused by the requested data missing the required thematic columns.")
            raise Exception("No shapefiles available to zip.")
        zip_cmd = self.zip_cmd.safe_substitute({'zipfile': zipfile, 'shp_dir': self.shapefile})
        proc = subprocess.Popen(zip_cmd, shell=True, executable='/bin/bash',
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = proc.communicate()
        returncode = proc.wait()
        if (returncode != 0):
            logger.error('{}:{}'.format(stdout, stderr))
            raise Exception('Error zipping shape directory. Exited with returncode: {0}'.format(returncode))
        if returncode == 0:
            # remove the shapefile directory
            shutil.rmtree(self.shapefile)
        if self.debug:
            print 'Zipped shapefiles: {0}'.format(self.shapefile)
        return zipfile
