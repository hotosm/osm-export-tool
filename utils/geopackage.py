# -*- coding: utf-8 -*-
import argparse
import logging
import os
import subprocess
from string import Template

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
DELETE FROM planet_osm_polygon where GeometryType(geom) == 'GEOMCOLLECTION';

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

-- add z_index columns
ALTER TABLE planet_osm_point ADD COLUMN z_index INTEGER(4) DEFAULT 0;
ALTER TABLE planet_osm_line ADD COLUMN z_index INTEGER(4) DEFAULT 0;
ALTER TABLE planet_osm_polygon ADD COLUMN z_index INTEGER(4) DEFAULT 0;
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

    def __init__(self, output_ini, points=[],lines=[],polygons=[]):
        """
        Initialize the OSMConfig utility.

        Args:
            categories: the export tags categorized by geometry type.
            job_name: the name of the job
        """
        self.points = points
        self.lines = lines
        self.polygons = polygons
        self.output_ini = output_ini

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

    def __init__(self, input_pbf, output_gpkg, temp_ini, feature_selection,aoi_geom,tempdir=None):
        """
        Initialize the OSMParser.

        Args:
            osm: the osm file to convert
            sqlite: the location of the sqlite output file.
        """
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.input_pbf = input_pbf
        self.output_gpkg = output_gpkg
        self.temp_ini = temp_ini
        self.feature_selection = feature_selection
        self.aoi_geom = aoi_geom
        
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
        key_union = self.feature_selection.key_union
        osmconf = OSMConfig(self.temp_ini,polygons=key_union,points=key_union,lines=key_union)
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
        conn.commit()

    @property
    def is_complete(self):
        return os.path.isfile(self.output_gpkg)

    @property
    def results(self):
        return [self.output_gpkg]


    #TODO this needs to be used
    def update_zindexes(self):
        # rewrite this to use SQLite instead of OGR driver.
        """
        Update the zindexes on sqlite layers.
        """
        ds = ogr.Open(self.output_gpkg, update=True)
        zindexes = {
            3: ('path', 'track', 'footway', 'minor', 'road', 'service', 'unclassified', 'residential'),
            4: ('tertiary_link', 'tertiary'),
            6: ('secondary_link', 'secondary'),
            7: ('primary_link', 'primary'),
            8: ('trunk_link', 'trunk'),
            9: ('motorway_link', 'motorway')
        }
        layer_count = ds.GetLayerCount()
        assert layer_count == 3, """Incorrect number of layers found. Run 'create_default_schema()' method first."""
        for layer_idx in range(layer_count):
            layer = ds.GetLayerByIndex(layer_idx).GetName()
            try:
                # update highway z_indexes
                for key in zindexes.keys():
                    sql = 'UPDATE {0} SET z_index = {1} WHERE highway IN {2};'.format(layer, key, zindexes[key])
                    ds.ExecuteSQL(sql)
            except RuntimeError:
                pass
            try:
                # update railway z_indexes
                sql = "UPDATE {0} SET z_index = z_index + 5 WHERE railway IS NOT NULL".format(layer)
                ds.ExecuteSQL(sql)
            except RuntimeError:
                pass
            try:
                # update layer
                sql = "UPDATE {0} SET z_index = z_index + 10 * cast(layer as int) WHERE layer IS NOT NULL".format(layer)
                ds.ExecuteSQL(sql)
            except RuntimeError:
                pass
            try:
                # update bridge z_index
                sql = "UPDATE {0} SET z_index = z_index + 10 WHERE bridge IN ('yes', 'true', 1)".format(layer)
                ds.ExecuteSQL(sql)
            except RuntimeError:
                pass
            try:
                # update tunnel z_index
                sql = "UPDATE {0} SET z_index = z_index - 10 WHERE tunnel IN ('yes', 'true', 1)".format(layer)
                ds.ExecuteSQL(sql)
            except RuntimeError:
                pass

        # close connection
        ds.Destroy()
