import logging
import os
import string
import argparse
from osgeo import ogr, osr, gdal
from django.utils import timezone
from django.utils import timezone
from datetime import datetime
from string import Template
from urllib2 import urlopen
from urllib2 import URLError

logger = logging.getLogger(__name__)

class Overpass(object):
    """
    Thin wrapper around an overpass query.
    Returns all nodes, ways and relations within the specified bounding box.
    """
    
    def __init__(self, url=None, bbox=None, osm=None, debug=False):
        self.url = 'http://localhost/interpreter' # default
        if url:
            self.url = url
        self.query_template = Template('(node($bbox);<;);out body;')
        if bbox:
            self.bbox = bbox
        else:
            raise Exception('A bounding box is required: miny,minx,maxy,maxx')
        if osm:
            self.osm = osm
        else:
            self.osm = 'query_out.osm' # in the current directory
        self.debug = debug

    def print_query(self,):
        q = self.query_template.safe_substitute({'bbox': self.bbox})
        print q
        
    
    def run_query(self,):
        q = self.query_template.safe_substitute({'bbox': self.bbox})
        if self.debug:
            print 'Query started at: %s' % datetime.now()
        try:
            with open(self.osm, 'w') as fd:
                f = urlopen(self.url, q)
                for line in f.readlines():
                    fd.write(line)
                f.close()
            fd.close()
        except URLError as e:
            raise Exception(e)
        if self.debug:
            print 'Query finished at %s' % datetime.now()
            print 'Wrote overpass query results to: %s' % self.osm


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Runs an overpass query using the provided bounding box')
    parser.add_argument('-o','--osm-file', required=False, dest="osm", help='The OSM file to write the query results to')
    parser.add_argument('-b','--bounding-box', required=True, dest="bbox",
                        help='A comma separated list of coordinates in the format: miny,minx,maxy,maxx')
    parser.add_argument('-u','--url', required=False, dest="url", help='The url endpoint of the overpass interpreter')
    parser.add_argument('-d','--debug', action="store_true", help="Turn on debug output")
    args = parser.parse_args()
    config = {}
    for k,v in vars(args).items():
        if (v == None): continue
        else:
           config[k] = v
    osm = config.get('osm')
    url = config.get('url')
    bbox = config.get('bbox')
    debug = False
    if config.get('debug'):
        debug = config.get('debug')
    overpass = Overpass(url=url, bbox=bbox, osm=osm, debug=debug)
    overpass.run_query()
    
    