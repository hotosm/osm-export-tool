# -*- coding: utf-8 -*-
from __future__ import with_statement

import argparse
import logging
import os
import shutil
import subprocess
from string import Template

logger = logging.getLogger(__name__)


class SQliteToShp(object):
    """
    Convert sqlite to shapefile.
    """

    def __init__(self, sqlite=None, shapefile=None, zipped=True, debug=False):
        """
        Initialize the SQliteToShp utility.

        Args:
            sqlite: the sqlite file to convert.
            shapefile: the path to the shapefile output
            zipped: whether to zip the output
        """
        self.sqlite = sqlite
        if not os.path.exists(self.sqlite):
            raise IOError('Cannot find sqlite file for this task.')
        self.shapefile = shapefile
        self.zipped = zipped
        if not self.shapefile:
            # create shp path from sqlite path.
            root = self.sqlite.split('.')[0]
            self.shapefile = root + 'shp'
        self.debug = debug
        self.cmd = Template("ogr2ogr -f 'ESRI Shapefile' $shp $sqlite -lco ENCODING=UTF-8")
        self.zip_cmd = Template("zip -j -r $zipfile $shp_dir")

    def convert(self, ):
        """
        Convert the sqlite to shape.
        """
        convert_cmd = self.cmd.safe_substitute({'shp': self.shapefile, 'sqlite': self.sqlite})
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
        Zip the shapefile output.
        """
        zipfile = self.shapefile + '.zip'
        zip_cmd = self.zip_cmd.safe_substitute({'zipfile': zipfile, 'shp_dir': self.shapefile})
        proc = subprocess.Popen(zip_cmd, shell=True, executable='/bin/bash',
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = proc.communicate()
        returncode = proc.wait()

        if (returncode != 0):
            logger.error('%s', stderr)
            raise Exception, 'Error zipping shape directory. Exited with returncode: {0}'.format(returncode)
        if returncode == 0:
            # remove the shapefile directory
            shutil.rmtree(self.shapefile)
        if self.debug:
            print 'Zipped shapefiles: {0}'.format(self.shapefile)
        return zipfile


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Converts a SQlite database to ESRI Shapefile.')
    parser.add_argument('-i', '--sqlite-file', required=True, dest="sqlite", help='The SQlite file to convert.')
    parser.add_argument('-o', '--shp-dir', required=True, dest="shp", help='The directory to write the Shapefile(s) to.')
    parser.add_argument('-z', '--zipped', action="store_true", help="Whether to zip the shapefile directory. Default true.")
    parser.add_argument('-d', '--debug', action="store_true", help="Turn on debug output")
    args = parser.parse_args()
    config = {}
    for k, v in vars(args).items():
        if (v == None):
            continue
        else:
            config[k] = v
    sqlite = config['sqlite']
    shapefile = config['shp']
    debug = False
    zipped = False
    if config.get('debug'):
        debug = True
    if config.get('zipped'):
        zipped = True
    s2s = SQliteToShp(sqlite=sqlite, shapefile=shapefile, debug=debug)
    s2s.convert()
