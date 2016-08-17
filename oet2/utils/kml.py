# -*- coding: utf-8 -*-
from __future__ import with_statement

import argparse
import logging
import os
import subprocess
from string import Template

logger = logging.getLogger(__name__)


class SQliteToKml(object):
    """
    Thin wrapper around ogr2ogr to convert sqlite to KML.
    """

    def __init__(self, sqlite=None, kmlfile=None, zipped=True, debug=False):
        """
        Initialize the SQliteToKml utility.

        Args:
            sqlite: the sqlite file to convert
            kmlfile: where to write the kml output
            zipped: whether to zip the output
            debug: turn debugging on / off
        """
        self.sqlite = sqlite
        if not os.path.exists(self.sqlite):
            raise IOError('Cannot find sqlite file for this task.')
        self.kmlfile = kmlfile
        self.zipped = zipped
        if not self.kmlfile:
            # create kml path from sqlite path.
            root = self.sqlite.split('.')[0]
            self.kmlfile = root + '.kml'
        self.debug = debug
        self.cmd = Template("ogr2ogr -f 'KML' $kmlfile $sqlite")
        self.zip_cmd = Template("zip -j $zipfile $kmlfile")

    def convert(self, ):
        """
        Convert sqlite to kml.
        """
        convert_cmd = self.cmd.safe_substitute({'kmlfile': self.kmlfile,
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
        if self.zipped and returncode == 0:
            kmzfile = self._zip_kml_file()
            return kmzfile
        else:
            return self.kmlfile

    def _zip_kml_file(self, ):
        """Zip the kml output file."""
        kmzfile = self.kmlfile.split('.')[0] + '.kmz'
        zip_cmd = self.zip_cmd.safe_substitute({'zipfile': kmzfile,
                                                'kmlfile': self.kmlfile})
        proc = subprocess.Popen(zip_cmd, shell=True, executable='/bin/bash',
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = proc.communicate()
        returncode = proc.wait()
        if returncode != 0:
            logger.error('%s', stderr)
            raise Exception, 'Failed to create zipfile for {0}'.format(self.kmlfile)
        if returncode == 0:
            # remove the kml file
            os.remove(self.kmlfile)
        if self.debug:
            print 'Zipped KML: {0}'.format(kmzfile)
        return kmzfile


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Converts a SQlite database to KML.')
    parser.add_argument('-i', '--sqlite-file', required=True,
                        dest="sqlite", help='The SQlite file to convert.')
    parser.add_argument('-k', '--kml-file', required=True,
                        dest="kmlfile", help='The KML file to write to.')
    parser.add_argument('-z', '--zipped', action="store_true",
                        help="Whether to zip the KML. Default true.")
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
    kmlfile = config['kmlfile']
    debug = False
    zipped = False
    if config.get('debug'):
        debug = True
    if config.get('zipped'):
        zipped = True
    s2k = SQliteToKml(sqlite=sqlite, kmlfile=kmlfile, zipped=zipped, debug=debug)
    s2k.convert()
