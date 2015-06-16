import logging
import os
import string
import argparse
import subprocess
from osgeo import ogr, osr, gdal
from datetime import datetime
from string import Template

logger = logging.getLogger(__name__)

class OSMParser(object):
    """
    Parses a OSM file (.osm or .pbf) dumped from overpass query.
    Creates an ouput spatialite file to be used in export pipeline.
    """
    
    def __init__(self, osm=None, sqlite=None, osmconf=None, schema=None, debug=None):
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.osm = osm
        self.sqlite = sqlite
        self.schema = schema
        self.debug = debug
        if osmconf:
            self.osmconf = osmconf
        else:
            self.osmconf = self.path + '/conf/test.ini'
            logger.debug(self.osmconf)
        """
            OGR Command to run.
            OSM_CONFIG_FILE determines which OSM keys should be translated into OGR layer fields.
            See osmconf.ini for details. See gdal config options at http://www.gdal.org/drv_osm.html
        """
        self.ogr_cmd = Template("""ogr2ogr -f SQlite -dsco SPATIALITE=YES $sqlite $osm \
                                    --config OSM_CONFIG_FILE $osmconf \
                                    --config OGR_INTERLEAVED_READING YES \
                                    --config OSM_MAX_TMPFILE_SIZE 100 -gt 65536
                                """)
        
        # Enable GDAL/OGR exceptions
        gdal.UseExceptions()
        self.srs = osr.SpatialReference()
        self.srs.ImportFromEPSG(4326) # configurable
        # create the output file
        self._init_spatialite()
        self._create_default_schema()
        self._update_zindexes()
        if self.schema:
            # run other schema transformations here...
            pass
        self._cleanup()
        
    def _init_spatialite(self, ):        
        # create spatialite from osm data
        ogr_cmd = self.ogr_cmd.safe_substitute({'sqlite': self.sqlite,
                                                'osm': self.osm, 'osmconf': self.osmconf})
        if(self.debug):
            print 'Running: %s' % ogr_cmd
        proc = subprocess.Popen(ogr_cmd, shell=True, executable='/bin/bash',
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = proc.communicate()
        if (stderr != None and stderr.startswith('ERROR')):
                self._cleanup()
                raise Exception, "ogr2ogr process failed with error: %s" % stderr.rstrip()   
        returncode = proc.wait()
        if(self.debug):
            print 'ogr2ogr returned: %s' % returncode
            
    def _create_default_schema(self, ):
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
        if self.debug:
            print 'spatialite returned: %s' % returncode
 
    def _update_zindexes(self):
        self.spatialite = ogr.Open(self.sqlite, update=True)
        zindexes = {
            3 : ('path', 'track', 'footway', 'minor', 'road', 'service', 'unclassified', 'residential'),
            4 : ('tertiary_link', 'tertiary'),
            6 : ('secondary_link', 'secondary'),
            7 : ('primary_link', 'primary'),
            8 : ('trunk_link', 'trunk'),
            9 : ('motorway_link', 'motorway')
        }
        for layer_idx in range(self.spatialite.GetLayerCount()):
            layer = self.spatialite.GetLayerByIndex(layer_idx).GetName()
            # update highway z_indexes
            for key in zindexes.keys():
                sql = 'UPDATE {0} SET z_index = {1} WHERE highway IN {2};'.format(layer, key, zindexes[key])
                self.spatialite.ExecuteSQL(sql)
            # update railway z_indexes
            sql = "UPDATE {0} SET z_index = z_index + 5 WHERE railway <> ''".format(layer);
            self.spatialite.ExecuteSQL(sql)
            # update layer
            sql = "UPDATE {0} SET z_index = z_index + 10 * cast(layer as int) WHERE layer <> ''".format(layer);
            self.spatialite.ExecuteSQL(sql)
            # update bridge z_index
            sql = "UPDATE {0} SET z_index = z_index + 10 WHERE bridge IN ('yes', 'true', 1)".format(layer);
            self.spatialite.ExecuteSQL(sql)
            # update tunnel z_index
            sql = "UPDATE {0} SET z_index = z_index - 10 WHERE tunnel IN ('yes', 'true', 1)".format(layer);
            self.spatialite.ExecuteSQL(sql)

    def _cleanup(self, ):
        # flush to disk
        if self.spatialite:
            self.spatialite.Destroy()
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="""Converts OSM (xml|pbf) to Spatialite.
                                                    Updates schema to create planet_osm_* tables.
                                                    Creates planet_osm_roads tables.
                                                    Updates z_indexes on all layers.""")
    parser.add_argument('-o','--osm-file', required=True, dest="osm", help='The OSM file to convert (xml or pbf)')
    parser.add_argument('-s','--spatialite-file', required=True, dest="sqlite", help='The sqlite output file')
    parser.add_argument('-q','--schema-sql', required=False, dest="schema", help='A sql file to refactor the output schema')
    parser.add_argument('-d','--debug', action="store_true", help="Turn on debug output")
    args = parser.parse_args()
    config = {}
    for k,v in vars(args).items():
        if (v == None): continue
        else:
           config[k] = v
    osm = config.get('osm')
    sqlite = config.get('sqlite')
    debug = False
    if config.get('debug'): debug = True
    OSMParser(osm=osm, sqlite=sqlite, debug=debug)