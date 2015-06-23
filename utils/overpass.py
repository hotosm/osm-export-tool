import logging
import os
import string
import argparse
from osgeo import ogr, osr, gdal
from django.utils import timezone
from django.utils import timezone
from datetime import datetime
from string import Template
import requests
from requests import exceptions

logger = logging.getLogger(__name__)

class Overpass(object):
    """
    Thin wrapper around an overpass query.
    Returns all nodes, ways and relations within the specified bounding box.
    """
    
    def __init__(self, url=None, bbox=None, osm=None, debug=False):
        self.url = 'http://localhost/interpreter' # default
        if url: self.url = url
        self.query_template = Template('(node($bbox);<;);out body;')
        if bbox:
            self.bbox = bbox
        else:
            raise Exception('A bounding box is required: miny,minx,maxy,maxx')
        if osm:
            self.osm = osm
        else:
            self.osm = 'query.osm' # in the current directory
        self.debug = debug

    def get_query(self,):
        q = self.query_template.safe_substitute({'bbox': self.bbox})
        return q
        
    def run_query(self,):
        q = self.get_query()
        if self.debug:
            print 'Query started at: %s' % datetime.now()   
        try:
            req = requests.post(self.url, data=q, stream=True)
            logger.debug(req)
            CHUNK = 16 * 1024 # whats the optimum here?
            with open(self.osm, 'wb') as fd:
                for chunk in req.iter_content(CHUNK):
                    fd.write(chunk)
        except exceptions.RequestException as e:
            logger.error('Overpass query threw: {0}'.format(e))
            raise exceptions.RequestException(e)
        if self.debug:
            print 'Query finished at %s' % datetime.now()
            print 'Wrote overpass query results to: %s' % self.osm
        return self.osm


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
    
    