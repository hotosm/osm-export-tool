# -*- coding: utf-8 -*-
import argparse
import logging
import os
import subprocess
from string import Template
from django.conf import settings

logger = logging.getLogger(__name__)


class PBFToMWM(object):
    """
    Thin wrapper around to convert pbf file to mwm.
    """
    def __init__( self, pbffile=None, mwmfile=None, debug=False):
        self.pbffile = pbffile
        if not os.path.exists(self.pbffile):
            raise IOError('Cannot find pbf file data for this task.')
        self.mwmfile = mwmfile
        if not self.mwmfile:
            # create mwm path from osm path.
            root = self.pbffile.rsplit('.', 1)[0]
            self.mwmfile = root + '.mwm' 
        self.debug = debug
        mwm_root_path = settings.EXPORT_MWM_ROOT
        self.cmd_mwm = Template( mwm_root_path + 'tools/unix/generate_mwm.sh $pbf')

    def convert(self, ):
        convert_cmd_mwm = self.cmd_mwm.safe_substitute({'pbf': self.pbffile})
        if(self.debug):
            print 'Running: %s' % convert_cmd_mwm
        proc_mwm = subprocess.Popen(convert_cmd_mwm, shell=True, executable='/bin/bash', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (_, stderr) = proc_mwm.communicate()
        returncode = proc_mwm.returncode
        if (returncode != 0):
            logger.error('%s', stderr)
            raise Exception, "generate_mwm failed with return code: {0}".format(returncode)
        if(self.debug):
            print 'generate_mwm returned: {0}'.format(returncode)
        return self.mwmfile

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Converts PBF XML to MWM')
    parser.add_argument('-p', '--pbf-file', required=True, dest="pbf", help='The PBF file to convert')
    parser.add_argument('-m', '--mwm-file', required=True, dest="mwm", help='The MWM file to write to')
    parser.add_argument('-d', '--debug', action="store_true", help="Turn on debug output")
    args = parser.parse_args()
    config = {}
    for k, v in vars(args).items():
        if (v == None):
            continue
        else:
            config[k] = v
    pbf_file = config['pbf']
    mwm_file = config['mwm']
    debug = False
    if config.get('debug'):
        debug = True
    p2m = PBFToMWM( pbffile=pbf_file, mwmfile=mwm_file, debug=debug)
    p2m.convert()
