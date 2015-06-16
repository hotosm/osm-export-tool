from __future__ import with_statement
import json
import logging
import argparse
import subprocess
import string
from string import Template

logger = logging.getLogger(__name__)

class OSMToPBF(object):
    """
    Thin wrapper around osmconvert to convert osm xml to pbf.
    """
    def __init__(self, osm=None, pbf=None, debug=False):
        self.osm = osm
        self.pbf = pbf
        self.debug = debug
        self.cmd = Template('osmconvert $osm --out-pbf >$pbf')

    def convert(self, ):
        convert_cmd = self.cmd.safe_substitute({'osm': self.osm,'pbf': self.pbf})
        if(self.debug):
            print 'Running: %s' % convert_cmd
        proc = subprocess.Popen(convert_cmd, shell=True, executable='/bin/bash', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout,stderr) = proc.communicate()
        if (stderr != None and stderr.startswith('osmconvert Error')):
            raise Exception, stderr.rstrip()  
        returncode = proc.wait()
        if(self.debug):
            print 'Osmconvert returned: %s' % returncode


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Converts OSM XML to PBF')
    parser.add_argument('-o','--osm-file', required=True, dest="osm", help='The OSM file to convert')
    parser.add_argument('-p','--pbf-file', required=True, dest="pbf", help='The PBF file to write to')
    parser.add_argument('-d','--debug', action="store_true", help="Turn on debug output")
    args = parser.parse_args()
    config = {}
    for k,v in vars(args).items():
        if (v == None): continue
        else:
           config[k] = v
    osm = config['osm']
    pbf = config['pbf']
    debug = False
    if config.get('debug'):
        debug = True
    o2p = OSMToPBF(osm=osm, pbf=pbf, debug=debug)
    o2p.convert()
    
        
    