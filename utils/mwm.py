# -*- coding: utf-8 -*-
import argparse
import logging
import os
import subprocess
from string import Template
from django.conf import settings

logger = logging.getLogger(__name__)


class OSMToMWM(object):
    """
    Thin wrapper around osmconvert to convert osm xml to mwm.
    """

    def __init__(self, osm=None, pbffile=None, mwmfile=None, debug=False):
        self.osm = osm
        if not os.path.exists(self.osm):
            raise IOError('Cannot find raw OSM data for this task.')
        self.pbffile = pbffile
        self.mwmfile = mwmfile
        if not self.pbffile:
            # create pbf path from osm path.
            root = self.osm.split('.')[0]
            self.pbffile = root + '.pbf' 
        if not self.mwmfile:
            # create mwm path from osm path.
            root = self.osm.split('.')[0]
            self.mwmfile = root + '.mwm' 
        self.debug = debug
        mwm_root_path = settings.EXPORT_MWM_ROOT
        self.cmd = Template('osmconvert $osm --out-pbf >$pbf')
        self.cmd_mwm = Template('DATA_PATH=' + mwm_root_path + 'data ' + mwm_root_path + 'generate_mwm.sh $pbf')

    def convert(self, ):
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
        convert_cmd_mwm = self.cmd_mwm.safe_substitute({'pbf': self.pbffile})
        if(self.debug):
            print 'Running: %s' % convert_cmd_mwm
        proc_mwm = subprocess.Popen(convert_cmd_mwm, shell=True, executable='/bin/bash', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = proc_mwm.communicate()
        returncode = proc_mwm.wait()
        if (returncode != 0):
            logger.error('%s', stderr)
            raise Exception, "generate_mwm failed with return code: {0}".format(returncode)
        if(self.debug):
            print 'generate_mwm returned: %s' % returncode
        return self.mwmfile

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Converts OSM XML to MWM')
    parser.add_argument('-o', '--osm-file', required=True, dest="osm", help='The OSM file to convert')
    parser.add_argument('-m', '--mwm-file', required=True, dest="mwm", help='The MWM file to write to')
    parser.add_argument('-d', '--debug', action="store_true", help="Turn on debug output")
    args = parser.parse_args()
    config = {}
    for k, v in vars(args).items():
        if (v == None):
            continue
        else:
            config[k] = v
    osm = config['osm']
    mwm_file = config['mwm']
    debug = False
    if config.get('debug'):
        debug = True
    o2p = OSMToMWM(osm=osm, mwmfile=mwm_file, debug=debug)
    o2p.convert()
