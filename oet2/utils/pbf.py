# -*- coding: utf-8 -*-
from __future__ import with_statement

import argparse
import logging
import os
import subprocess
from string import Template

logger = logging.getLogger(__name__)


class OSMToPBF(object):
    """
    Convert OSM to PBF.
    """

    def __init__(self, osm=None, pbffile=None, debug=False):
        """
        Initialize the OSMToPBF utility.

        Args:
            osm: the raw osm file to convert
            pbffile: the location of the pbf output file
        """
        self.osm = osm
        if not os.path.exists(self.osm):
            raise IOError('Cannot find raw OSM data for this task.')
        self.pbffile = pbffile
        if not self.pbffile:
            # create pbf path from osm path.
            root = self.osm.split('.')[0]
            self.pbffile = root + '.pbf'
        self.debug = debug
        self.cmd = Template('osmconvert $osm --out-pbf >$pbf')

    def convert(self, ):
        """
        Convert the raw osm to pbf.
        """
        convert_cmd = self.cmd.safe_substitute({'osm': self.osm, 'pbf': self.pbffile})
        if(self.debug):
            print 'Running: %s' % convert_cmd
        proc = subprocess.Popen(convert_cmd, shell=True, executable='/bin/bash', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = proc.communicate()
        returncode = proc.wait()
        if (returncode != 0):
            logger.error('%s', stderr)
            raise Exception, "osmconvert failed with return code: {0}".format(returncode)
        if(self.debug):
            print 'Osmconvert returned: %s' % returncode
        return self.pbffile


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Converts OSM XML to PBF')
    parser.add_argument('-o', '--osm-file', required=True, dest="osm", help='The OSM file to convert')
    parser.add_argument('-p', '--pbf-file', required=True, dest="pbf", help='The PBF file to write to')
    parser.add_argument('-d', '--debug', action="store_true", help="Turn on debug output")
    args = parser.parse_args()
    config = {}
    for k, v in vars(args).items():
        if (v == None):
            continue
        else:
            config[k] = v
    osm = config['osm']
    pbf = config['pbf']
    debug = False
    if config.get('debug'):
        debug = True
    o2p = OSMToPBF(osm=osm, pbf=pbf, debug=debug)
    o2p.convert()
