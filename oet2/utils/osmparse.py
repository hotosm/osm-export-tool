# -*- coding: utf-8 -*-
import argparse
import logging
import os
import subprocess
from string import Template

from osgeo import gdal, ogr, osr

logger = logging.getLogger(__name__)


class OSMParser(object):
    """
    Parse a OSM file (.osm or .pbf) dumped from overpass query.
    Creates an ouput spatialite file to be used in export pipeline.
    """

    def __init__(self, osm=None, sqlite=None, osmconf=None, debug=None):
        """
        Initialize the OSMParser.

        Args:
            osm: the osm file to convert
            sqlite: the location of the sqlite output file.
            debug: turn on / off debug output.
        """
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.osm = osm
        if not os.path.exists(self.osm):
            raise IOError('Cannot find PBF data for this task.')
        self.sqlite = sqlite
        self.debug = debug
        if osmconf:
            self.osmconf = osmconf
        else:
            self.osmconf = self.path + '/conf/hotosm.ini'
            logger.debug('Found osmconf ini file at: {0}'.format(self.osmconf))
        """
        OGR Command to run.
        OSM_CONFIG_FILE determines which OSM keys should be translated into OGR layer fields.
        See osmconf.ini for details. See gdal config options at http://www.gdal.org/drv_osm.html
        """
        self.ogr_cmd = Template("""
            ogr2ogr -f SQlite -dsco SPATIALITE=YES $sqlite $osm \
            --config OSM_CONFIG_FILE $osmconf \
            --config OGR_INTERLEAVED_READING YES \
            --config OSM_MAX_TMPFILE_SIZE 100 -gt 65536
        """)

        # Enable GDAL/OGR exceptions
        gdal.UseExceptions()
        self.srs = osr.SpatialReference()
        self.srs.ImportFromEPSG(4326)  # configurable

    def create_spatialite(self, ):
        """
        Create the spatialite file from the osm data.
        """
        ogr_cmd = self.ogr_cmd.safe_substitute({'sqlite': self.sqlite,
                                                'osm': self.osm, 'osmconf': self.osmconf})
        if(self.debug):
            print 'Running: %s' % ogr_cmd
        proc = subprocess.Popen(ogr_cmd, shell=True, executable='/bin/bash',
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = proc.communicate()
        returncode = proc.wait()
        if returncode != 0:
            logger.error('%s', stderr)
            raise Exception, "ogr2ogr process failed with returncode: {0}".format(returncode)
        if(self.debug):
            print 'ogr2ogr returned: %s' % returncode

    def create_default_schema(self, ):
        """
        Create the default osm sqlite schema.

        Creates planet_osm_point, planet_osm_line, planet_osm_polygon tables.
        """
        assert os.path.exists(self.sqlite), "No spatialite file. Run 'create_spatialite()' method first."
        # update the spatialite schema
        self.update_sql = Template("spatialite $sqlite < $update_sql")
        sql_cmd = self.update_sql.safe_substitute({'sqlite': self.sqlite,
                            'update_sql': self.path + '/sql/planet_osm_schema.sql'})
        if(self.debug):
            print 'Running: %s' % sql_cmd
        proc = subprocess.Popen(sql_cmd, shell=True, executable='/bin/bash',
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = proc.communicate()
        returncode = proc.wait()
        if returncode != 0:
            logger.error('%s', stderr)
            raise Exception, "{0} process failed with returncode: {1}".format(sql_cmd, returncode)
        if self.debug:
            print 'spatialite returned: %s' % returncode

    def update_zindexes(self, ):
        """
        Update the zindexes on sqlite layers.
        """
        assert os.path.exists(self.sqlite), "No spatialite file. Run 'create_spatialite()' method first."
        ds = ogr.Open(self.sqlite, update=True)
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
                sql = "UPDATE {0} SET z_index = z_index + 5 WHERE railway <> ''".format(layer)
                ds.ExecuteSQL(sql)
            except RuntimeError:
                pass
            try:
                # update layer
                sql = "UPDATE {0} SET z_index = z_index + 10 * cast(layer as int) WHERE layer <> ''".format(layer)
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=(
            'Converts OSM (xml|pbf) to Spatialite. \n'
            'Updates schema to create planet_osm_* tables.\n'
            'Updates z_indexes on all layers.'
        )
    )
    parser.add_argument('-o', '--osm-file', required=True, dest="osm", help='The OSM file to convert (xml or pbf)')
    parser.add_argument('-s', '--spatialite-file', required=True, dest="sqlite", help='The sqlite output file')
    parser.add_argument('-q', '--schema-sql', required=False, dest="schema", help='A sql file to refactor the output schema')
    parser.add_argument('-d', '--debug', action="store_true", help="Turn on debug output")
    args = parser.parse_args()
    config = {}
    for k, v in vars(args).items():
        if (v == None):
            continue
        else:
            config[k] = v
    osm = config.get('osm')
    sqlite = config.get('sqlite')
    debug = False
    if config.get('debug'):
        debug = True
    parser = OSMParser(osm=osm, sqlite=sqlite, debug=debug)
    parser.create_spatialite()
    parser.create_default_schema()
    parser.update_zindexes()
