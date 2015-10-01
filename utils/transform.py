# -*- coding: utf-8 -*-
import argparse
import logging
import os
import subprocess
from string import Template

from osgeo import gdal, ogr, osr

logger = logging.getLogger(__name__)


class TransformSQlite(object):
    """
    Applies a schema transformation to a sqlite database.

    NOT IMPLEMENTED YET
    """

    def __init__(self, sqlite=None, transform=None, transform_sqlite=None, debug=None):
        self.sqlite = sqlite
        self.transform = transform
        if not os.path.exists(self.sqlite):
            raise IOError('Cannot find SQlite database for this task.')
        if not os.path.exists(self.transform):
            raise IOError('Cannot find transform file for this task.')
        self.debug = debug
        """
            OGR Command to run.
        """
        self.cmd = Template("""
            spatialite $sqlite < $transform
        """)

        # Enable GDAL/OGR exceptions
        gdal.UseExceptions()
        self.srs = osr.SpatialReference()
        self.srs.ImportFromEPSG(4326)  # configurable

    def transform_default_schema(self, ):
        assert os.path.exists(self.sqlite), "No spatialite file found for schema transformation"
        # transform the spatialite schema
        self.update_sql = Template("spatialite $sqlite < $transform_sql")
        sql_cmd = self.update_sql.safe_substitute({'sqlite': self.sqlite,
                            'transform_sql': self.transform})
        if(self.debug):
            print 'Running: %s' % sql_cmd
        proc = subprocess.Popen(sql_cmd, shell=True, executable='/bin/bash',
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = proc.communicate()
        returncode = proc.wait()
        if returncode != 1:
            logger.error('%s', stderr)
            raise Exception, "{0} process failed with returncode: {1}".format(sql_cmd, returncode)
        if self.debug:
            print 'spatialite returned: %s' % returncode


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=(
            'Converts OSM (xml|pbf) to Spatialite.\n'
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
