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
    Wrapper around an Overpass query.
    Returns all nodes, ways and relations within the specified bounding box
    and filtered by the provided tags.
    Reverts to default query if no tags supplied.
    """
    
    def __init__(self, url=None, bbox=None, osm=None, tags=None, debug=False):
        self.url = 'http://localhost/interpreter' # default
        self.default_template = Template('(node($bbox);<;);out body;')
        self.query = None
        if url: self.url = url
        if bbox:
            self.bbox = bbox
        else:
            raise Exception('A bounding box is required: miny,minx,maxy,maxx')
        if tags and len(tags) > 0:
            self.tags = tags
            self.query = self._build_overpass_query()
        else:
            self.query = self.default_template.safe_substitute({'bbox': self.bbox})
        if osm:
            self.osm = osm
        else:
            self.osm = 'query.osm' # in the current directory
        self.debug = debug
        
    
    def get_query(self,):
        return self.query
        
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
    
    def _build_overpass_query(self, ):
        
        template = Template("""
                [out:xml];
                (
                  $nodes
                  $ways
                  $relations
                );
                out body qt;
                >;
                out skel qt;
            """)

        nodes = []
        ways = []
        relations = []
        keys = []
        
        node_tmpl = Template('node[$tags]($bbox);')
        way_tmpl = Template('way[$tags]($bbox);')
        rel_tmpl = Template('rel[$tags]($bbox);')
        
        for tag in self.tags:
            try:
                (k, v) = tag.split(':')
                keys.append(k)
                tag_str = '"' + k  + '"="' + v + '"'
                node_tag = node_tmpl.safe_substitute({'tags': tag_str, 'bbox': self.bbox})
                way_tag = way_tmpl.safe_substitute({'tags': tag_str, 'bbox': self.bbox})
                rel_tag = rel_tmpl.safe_substitute({'tags': tag_str, 'bbox': self.bbox})
                nodes.append(node_tag)
                ways.append(way_tag)
                relations.append(rel_tag)
            except ValueError as e:
                continue
        # build strings
        node_filter = '\n'.join(nodes)
        way_filter = '\n'.join(ways)
        rel_filter = '\n'.join(relations)
        unique_keys = []
        for key in keys:
            if key not in unique_keys:
                unique_keys.append(key)
        logger.debug(','.join(unique_keys))
        
        q = template.safe_substitute({'nodes': node_filter, 'ways': way_filter,
                                                 'relations': rel_filter})
    
        return q    



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
    
    