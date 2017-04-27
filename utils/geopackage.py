# -*- coding: utf-8 -*-
import argparse
import logging
import os
import subprocess
from string import Template
from artifact import Artifact

from osgeo import gdal, ogr, osr
import sqlite3

LOG = logging.getLogger(__name__)


SPATIAL_SQL = '''
UPDATE 'points' SET geom=GeomFromGPB(geom);
UPDATE 'lines' SET geom=GeomFromGPB(geom);
UPDATE 'multipolygons' SET geom=GeomFromGPB(geom);

UPDATE points SET geom = (SELECT ST_Intersection(boundary.geom,p.geom) FROM boundary,points p WHERE points.fid = p.fid);
UPDATE lines SET geom = (SELECT ST_Intersection(boundary.geom,l.geom) FROM boundary,lines l WHERE lines.fid = l.fid);
UPDATE multipolygons SET geom = (SELECT ST_Intersection(boundary.geom,m.geom) FROM boundary,multipolygons m WHERE multipolygons.fid = m.fid);

DELETE FROM points where geom IS NULL;
DELETE FROM lines where geom IS NULL;
DELETE FROM multipolygons where geom IS NULL;


ALTER TABLE points RENAME TO planet_osm_point;
ALTER TABLE lines RENAME TO planet_osm_line;
ALTER TABLE multipolygons RENAME TO planet_osm_polygon;

DROP TRIGGER rtree_multipolygons_geom_delete;
DROP TRIGGER rtree_multipolygons_geom_insert;
DROP TRIGGER rtree_multipolygons_geom_update1;
DROP TRIGGER rtree_multipolygons_geom_update2;
DROP TRIGGER rtree_multipolygons_geom_update3;
DROP TRIGGER rtree_multipolygons_geom_update4;
DROP TRIGGER rtree_points_geom_delete;
DROP TRIGGER rtree_points_geom_insert;
DROP TRIGGER rtree_points_geom_update1;
DROP TRIGGER rtree_points_geom_update2;
DROP TRIGGER rtree_points_geom_update3;
DROP TRIGGER rtree_points_geom_update4;
DROP TRIGGER rtree_lines_geom_delete;
DROP TRIGGER rtree_lines_geom_insert;
DROP TRIGGER rtree_lines_geom_update1;
DROP TRIGGER rtree_lines_geom_update2;
DROP TRIGGER rtree_lines_geom_update3;
DROP TRIGGER rtree_lines_geom_update4;

-- TODO: these are invalid multipolygons that result in GeometryCollections of linear features.
-- see https://github.com/hotosm/osm-export-tool2/issues/155 for discussion.
-- maybe we should log these somewhere.
DELETE FROM planet_osm_polygon where GeometryType(geom) NOT IN ('POLYGON','MULTIPOLYGON');

SELECT gpkgAddSpatialIndex('boundary', 'geom');
SELECT gpkgAddSpatialIndex('planet_osm_point', 'geom');
SELECT gpkgAddSpatialIndex('planet_osm_line', 'geom');
SELECT gpkgAddSpatialIndex('planet_osm_polygon', 'geom');

UPDATE 'boundary' SET geom=AsGPB(geom);
UPDATE 'planet_osm_point' SET geom=AsGPB(geom);
UPDATE 'planet_osm_line' SET geom=AsGPB(geom);
UPDATE 'planet_osm_polygon' SET geom=AsGPB(geom);

DROP TABLE multilinestrings;
DROP TABLE other_relations;
DROP TABLE rtree_lines_geom;
DROP TABLE rtree_multilinestrings_geom;
DROP TABLE rtree_multipolygons_geom;
DROP TABLE rtree_other_relations_geom;
DROP TABLE rtree_points_geom;

INSERT INTO gpkg_contents VALUES ('boundary', 'features', 'boundary', '', '2017-04-08T01:35:16.576Z', null, null, null, null, '4326');
INSERT INTO gpkg_geometry_columns VALUES ('boundary', 'geom', 'MULTIPOLYGON', '4326', '0', '0');
UPDATE gpkg_contents SET table_name = "planet_osm_point",identifier = "planet_osm_point" WHERE table_name = "points";
UPDATE gpkg_geometry_columns SET table_name = "planet_osm_point" WHERE table_name = "points";
UPDATE gpkg_contents SET table_name = "planet_osm_line",identifier = "planet_osm_line" WHERE table_name = "lines";
UPDATE gpkg_geometry_columns SET table_name = "planet_osm_line" WHERE table_name = "lines";
UPDATE gpkg_contents SET table_name = "planet_osm_polygon", identifier = "planet_osm_polygon" WHERE table_name = "multipolygons";
UPDATE gpkg_geometry_columns SET table_name = "planet_osm_polygon" WHERE table_name = "multipolygons";
DELETE FROM gpkg_contents WHERE table_name="multilinestrings";
DELETE FROM gpkg_geometry_columns WHERE table_name="multilinestrings";
DELETE FROM gpkg_contents WHERE table_name="other_relations";
DELETE FROM gpkg_geometry_columns WHERE table_name="other_relations";
DELETE FROM gpkg_extensions WHERE table_name="multilinestrings";
DELETE FROM gpkg_extensions WHERE table_name="other_relations";
DELETE FROM gpkg_geometry_columns WHERE table_name="multilinestrings";
DELETE FROM gpkg_geometry_columns WHERE table_name="other_relations";
'''


INI_TEMPLATE = '''
# Configuration file for OSM import

# put here the name of keys for ways that are assumed to be polygons if they are closed
# see http://wiki.openstreetmap.org/wiki/Map_Features
closed_ways_are_polygons=aeroway,amenity,boundary,building,craft,geological,harbour,historic,landuse,leisure,man_made,military,natural,office,place,power,shop,sport,tourism,water,waterway,wetland

# laundering of keys ( ':' turned into '_' )
attribute_name_laundering=no

# uncomment to report all nodes, including the ones without any (significant) tag
#report_all_nodes=yes

# uncomment to report all ways, including the ones without any (significant) tag
#report_all_ways=yes

[points]
# common attributes
osm_id=yes
osm_version=no
osm_timestamp=no
osm_uid=no
osm_user=no
osm_changeset=no

# keys to report as OGR fields
attributes={points_attributes}

# keys that, alone, are not significant enough to report a node as a OGR point
unsignificant=created_by,converted_by,source,time,attribution
# keys that should NOT be reported in the "other_tags" field
ignore=created_by,converted_by,source,time,note,openGeoDB:,fixme,FIXME
# uncomment to avoid creation of "other_tags" field
other_tags=no
# uncomment to create "all_tags" field. "all_tags" and "other_tags" are exclusive
#all_tags=no

[lines]
# common attributes
osm_id=yes
osm_version=no
osm_timestamp=no
osm_uid=no
osm_user=no
osm_changeset=no

# keys to report as OGR fields
attributes={lines_attributes}
# keys that should NOT be reported in the "other_tags" field
ignore=created_by,converted_by,source,time,ele,note,openGeoDB:,fixme,FIXME
# uncomment to avoid creation of "other_tags" field
other_tags=no
# uncomment to create "all_tags" field. "all_tags" and "other_tags" are exclusive
#all_tags=yes

[multipolygons]
# common attributes
# note: for multipolygons, osm_id=yes instanciates a osm_id field for the id of relations
# and a osm_way_id field for the id of closed ways. Both fields are exclusively set.
osm_id=yes
osm_version=no
osm_timestamp=no
osm_uid=no
osm_user=no
osm_changeset=no

# keys to report as OGR fields
attributes={multipolygons_attributes}
# keys that should NOT be reported in the "other_tags" field
ignore=area,created_by,converted_by,source,time,ele,note,openGeoDB:,fixme,FIXME
# uncomment to avoid creation of "other_tags" field
other_tags=no
# uncomment to create "all_tags" field. "all_tags" and "other_tags" are exclusive
#all_tags=yes

[multilinestrings]
# common attributes
osm_id=yes
osm_version=no
osm_timestamp=no
osm_uid=no
osm_user=no
osm_changeset=no

# keys to report as OGR fields
#attributes=access,addr:housename,addr:housenumber,addr:interpolation,admin_level,aerialway,barrier,bridge,boundary,construction,covered,cutting,denomination,disused,embankment,foot,generator:source,highway,junction,layer,lock,motorcar,name,natural,oneway,poi,population,railway,ref,religion,route,service,surface,toll,tower:type,tunnel,waterway,width,wood
# keys that should NOT be reported in the "other_tags" field
ignore=area,created_by,converted_by,source,time,ele,note,openGeoDB:,fixme,FIXME
# uncomment to avoid creation of "other_tags" field
other_tags=no
# uncomment to create "all_tags" field. "all_tags" and "other_tags" are exclusive
#all_tags=yes

[other_relations]
# common attributes
osm_id=yes
osm_version=no
osm_timestamp=no
osm_uid=no
osm_user=no
osm_changeset=no

# keys to report as OGR fields
#attributes=admin_level,aeroway,amenity,boundary,harbour,historic,landuse,leisure,man_made,military,name,natural,power,place,shop,sport,tourism,type,water,waterway,wetland,unocha:pcode
# keys that should NOT be reported in the "other_tags" field
ignore=area,created_by,converted_by,time,ele,note,openGeoDB:,fixme,FIXME
# uncomment to avoid creation of "other_tags" field
other_tags=no
# uncomment to create "all_tags" field. "all_tags" and "other_tags" are exclusive
#all_tags=yes
'''



class OSMConfig(object):
    """
    Create ogr2ogr OSM conf file based on the template
    at utils/conf/hotosm.ini.tmpl

    See: http://www.gdal.org/drv_osm.html
    """

    def __init__(self, stage_dir, points=[],lines=[],polygons=[]):
        """
        Initialize the OSMConfig utility.

        Args:
            categories: the export tags categorized by geometry type.
            job_name: the name of the job
        """
        self.points = points
        self.lines = lines
        self.polygons = polygons
        self.output_ini = stage_dir + "/osmconf.ini"

    def create_osm_conf(self, stage_dir=None):
        """
        Create the osm configuration file.

        Args:
            stage_dir: where to stage the config file.

        Return:
            the path to the export configuration file.
        """
        result = INI_TEMPLATE.format(
            points_attributes=','.join(self.points),
            lines_attributes=','.join(self.lines),
            multipolygons_attributes=','.join(self.polygons)
        )
        with open(self.output_ini, 'wb') as f:
            f.write(result)
        return self.output_ini


class Geopackage(object):
    """
    Parse a OSM file (.osm or .pbf) dumped from overpass query.
    Creates an output GeoPackage file to be used in export pipeline.
    """
    name = "geopackage"
    description = 'GeoPackage (OSM Schema)'

    @property
    def results(self):
        return [self.output_gpkg]

    def __init__(self, input_pbf, output_gpkg, stage_dir, feature_selection,aoi_geom,tempdir=None,per_theme=False):
        """
        Initialize the OSMParser.

        Args:
            osm: the osm file to convert
            sqlite: the location of the sqlite output file.
        """
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.input_pbf = input_pbf
        self.output_gpkg = output_gpkg
        self.stage_dir = stage_dir
        self.feature_selection = feature_selection
        self.aoi_geom = aoi_geom
        self.per_theme = per_theme
        
        """
        OGR Command to run.
        OSM_CONFIG_FILE determines which OSM keys should be translated into OGR layer fields.
        See osmconf.ini for details. See gdal config options at http://www.gdal.org/drv_osm.html
        """
        self.ogr_cmd = Template("""
            ogr2ogr -f GPKG $gpkg $osm \
            --config OSM_CONFIG_FILE $osmconf \
            --config OGR_INTERLEAVED_READING YES \
            --config OSM_MAX_TMPFILE_SIZE 100 -gt 65536
        """)

        # Enable GDAL/OGR exceptions
        gdal.UseExceptions()
        self.srs = osr.SpatialReference()
        self.srs.ImportFromEPSG(4326)  # configurable

    def run(self):
        """
        Create the GeoPackage from the osm data.
        """
        if self.is_complete:
            LOG.debug("Skipping Geopackage, file exists")
            return
        keys_points = self.feature_selection.key_union('points')
        keys_lines = self.feature_selection.key_union('lines')
        keys_polygons = self.feature_selection.key_union('polygons')
        osmconf = OSMConfig(self.stage_dir,points=keys_points,lines=keys_lines,polygons=keys_polygons)
        conf = osmconf.create_osm_conf()
        ogr_cmd = self.ogr_cmd.safe_substitute({'gpkg': self.output_gpkg,
                                                'osm': self.input_pbf, 'osmconf': conf})
        LOG.debug('Running: %s' % ogr_cmd)
        subprocess.check_call(ogr_cmd, shell=True, executable='/bin/bash')

        """
        Create the default osm gpkg schema
        Creates planet_osm_point, planet_osm_line, planet_osm_polygon tables
        """
        conn = sqlite3.connect(self.output_gpkg)
        conn.enable_load_extension(True)
        cur = conn.cursor()
        cur.execute("select load_extension('mod_spatialite')")
        cur.execute("CREATE TABLE boundary (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, geom GEOMETRY)");
        cur.execute("INSERT INTO boundary (geom) VALUES (GeomFromWKB(?,4326));",(self.aoi_geom.wkb,))
        cur.executescript(SPATIAL_SQL)
        self.update_zindexes(cur,self.feature_selection)

        # add themes
        create_sqls, index_sqls = self.feature_selection.sqls
        for query in create_sqls:
            LOG.debug(query)
            cur.execute(query)
        for query in index_sqls:
            LOG.debug(query)
            cur.executescript(query)
        conn.commit()
        conn.close()

        if self.per_theme:
            # this creates per-theme GPKGs
            WKT_TYPE_MAP = {
                'points':'POINT',
                'lines':'MULTILINESTRING',
                'polygons':'MULTIPOLYGON'
            }
            for theme in self.feature_selection.themes:
                conn = sqlite3.connect(self.stage_dir + theme + ".gpkg")
                conn.enable_load_extension(True)
                cur = conn.cursor()
                cur.execute("attach database ? as 'geopackage'",(self.output_gpkg,))
                cur.execute("create table gpkg_spatial_ref_sys as select * from geopackage.gpkg_spatial_ref_sys")
                cur.execute("create table gpkg_contents as select * from geopackage.gpkg_contents where 0")
                cur.execute("create table gpkg_geometry_columns as select * from geopackage.gpkg_geometry_columns where 0")
                for geom_type in self.feature_selection.geom_types(theme):
                    table_name = theme + "_" + geom_type
                    cur.execute("create table {0} as select * from geopackage.{0}".format(table_name))
                    cur.execute("INSERT INTO gpkg_contents VALUES ('{0}', 'features', '{0}', '', '2017-04-08T01:35:16.576Z', null, null, null, null, '4326')".format(table_name))
                    cur.execute("INSERT INTO gpkg_geometry_columns VALUES ('{0}', 'geom', '{1}', '4326', '0', '0')".format(table_name,WKT_TYPE_MAP[geom_type]))
                conn.commit()
                conn.close()

    @property
    def is_complete(self):
        return os.path.isfile(self.output_gpkg)

    @property
    def results(self):
        results_list = []
        for theme in self.feature_selection.themes:
            results_list.append(Artifact([os.path.join(self.stage_dir,theme) + ".gpkg"],Geopackage.name,theme=theme))
        return results_list


    def update_zindexes(self,cur,feature_selection):
        # arguably, determing Z-index should require all 5 of these OSM keys
        # to construct a consistent z-index.
        for geom_type in ['point','line','polygon']:
            key_union = feature_selection.key_union(geom_type + 's') # boo
            table_name = "planet_osm_" + geom_type
            if any([x in key_union for x in ['highway','railway','layer','bridge','tunnel']]):
                cur.execute("ALTER TABLE {table} ADD COLUMN z_index INTEGER(4) DEFAULT 0;".format(table=table_name))
                if "highway" in key_union:
                    cur.executescript("""
                        UPDATE {table} SET z_index = 3 WHERE highway IN ('path', 'track', 'footway', 'minor', 'road', 'service', 'unclassified', 'residential');
                        UPDATE {table} SET z_index = 4 WHERE highway IN ('tertiary_link', 'tertiary');
                        UPDATE {table} SET z_index = 6 WHERE highway IN ('secondary_link', 'secondary');
                        UPDATE {table} SET z_index = 7 WHERE highway IN ('primary_link', 'primary');
                        UPDATE {table} SET z_index = 8 WHERE highway IN  ('trunk_link', 'trunk');
                        UPDATE {table} SET z_index = 9 WHERE highway IN  ('motorway_link', 'motorway');
                    """.format(table=table_name))
                if "railway" in key_union:
                    cur.execute("UPDATE {table} SET z_index = z_index + 5 WHERE railway IS NOT NULL".format(table=table_name))
                if "layer" in key_union:
                    cur.execute("UPDATE {table} SET z_index = z_index + 10 * cast(layer as int) WHERE layer IS NOT NULL".format(table=table_name))
                if "bridge" in key_union:
                    cur.execute("UPDATE {table} SET z_index = z_index + 10 WHERE bridge IN ('yes', 'true', 1)".format(table=table_name))
                if "tunnel" in key_union:
                    cur.execute("UPDATE {table} SET z_index = z_index - 10 WHERE tunnel IN ('yes', 'true', 1)".format(table=table_name))
