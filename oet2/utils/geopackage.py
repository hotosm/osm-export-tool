# -*- coding: utf-8 -*-
from __future__ import with_statement

import argparse
import logging
import os
import subprocess
from string import Template

logger = logging.getLogger(__name__)


class SQliteToGeopackage(object):
    """
    Thin wrapper around ogr2ogr to convert sqlite to KML.
    """

    def __init__(self, sqlite=None, gpkgfile=None, debug=True):
        """
        Initialize the SQliteToKml utility.

        Args:
            sqlite: the sqlite file to convert
            gpkgfile: where to write the gpkg output
            debug: turn debugging on / off
        """
        self.sqlite = sqlite
        if not os.path.exists(self.sqlite):
            raise IOError('Cannot find sqlite file for this task.')
        self.gpkgfile = gpkgfile
        if not self.gpkgfile:
            # create gpkg path from sqlite path.
            root = self.sqlite.split('.')[0]
            self.gpkgfile = root + '.gkpg'
        self.debug = debug
        self.cmd = Template("ogr2ogr -f 'GPKG' $gpkgfile $sqlite")

    def convert(self, ):
        """
        Convert sqlite to gpkg.
        """
        convert_cmd = self.cmd.safe_substitute({'gpkgfile': self.gpkgfile,
                                                'sqlite': self.sqlite})
        if(self.debug):
            print 'Running: %s' % convert_cmd
        proc = subprocess.Popen(convert_cmd, shell=True, executable='/bin/bash',
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = proc.communicate()
        returncode = proc.wait()
        if (returncode != 0):
            logger.error('%s', stderr)
            raise Exception, "ogr2ogr process failed with returncode: {0}".format(returncode)
        if(self.debug):
            print 'ogr2ogr returned: %s' % returncode
        return self.gpkgfile


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Converts a SQlite database to GPKG.')
    parser.add_argument('-i', '--sqlite-file', required=True,
                        dest="sqlite", help='The SQlite file to convert.')
    parser.add_argument('-g', '--gpkg-file', required=True,
                        dest="gpkgfile", help='The GPKG file to write to.')
    parser.add_argument('-d', '--debug', action="store_true",
                        help="Turn on debug output")
    args = parser.parse_args()
    config = {}
    for k, v in vars(args).items():
        if (v == None):
            continue
        else:
            config[k] = v
    sqlite = config['sqlite']
    gpkgfile = config['gpkgfile']
    debug = False
    zipped = False
    if config.get('debug'):
        debug = True
    if config.get('zipped'):
        zipped = True
    s2g = SQliteToGeopackage(sqlite=sqlite, gpkgfile=gpkgfile, debug=debug)
    s2g.convert()
