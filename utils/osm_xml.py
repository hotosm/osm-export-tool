# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from string import Template
import os

import requests
from requests import exceptions
from artifact import Artifact

LOG = logging.getLogger(__name__)

class EmptyOsmXmlException(Exception):
    pass

class OverpassErrorException(Exception):
    pass

class OSM_XML(object):
    """
    Wrapper around an Overpass query.

    Returns all nodes, ways and relations within the specified bounding box
    and filtered by the provided tags.
    """


    name = "osm_xml"
    description = 'OSM XML'
    basic_template = Template('[maxsize:$maxsize][timeout:$timeout];(node($geom);<;>>;>;);out meta;')
    filter_template = Template("""[maxsize:$maxsize][timeout:$timeout];(
            (
                $nodes
            );
            (
                $ways
            );>;
            (
                $relations
            );>>;>;
            );out meta;""")

    def __init__(self, aoi_geom, output_xml, feature_selection=None,
                url='http://overpass-api.de/api/',
                overpass_max_size=4294967296,
                timeout=3200):
        """
        Initialize the Overpass utility.

        Args:
            bbox: the bounding box to extract
            stage_dir: where to stage the extract job
        """
        self.url = url
        self.output_xml = output_xml
        self.aoi_geom = aoi_geom
        self.overpass_max_size = overpass_max_size
        self.timeout = timeout
        self.feature_selection = feature_selection

    def raise_if_bad(self):
        with open(self.output_xml,'rb') as fd:
            sample = fd.readlines(8)
            if "<remark>" in ''.join(sample):
                raise OverpassErrorException(sample)

    def run(self):
        if self.is_complete:
            self.raise_if_bad()
            LOG.debug("Skipping OSM_XML, file exists")
            return
        """
        Return the export extents in order required by Overpass API.
        """
        args = {
            'maxsize': self.overpass_max_size,
            'timeout': self.timeout,
        }

        geom = None
        if self.aoi_geom.geom_type == 'MultiPolygon':
            extent = self.aoi_geom.extent  # (w,s,e,n)
            west = max(extent[0], -180)
            south = max(extent[1], -90)
            east = min(extent[2], 180)
            north = min(extent[3], 90)

            # overpass needs extents in order (s,w,n,e) and from -180 to 180,
            # -90 to 90
            geom = '{1},{0},{3},{2}'.format(west, south, east, north)
        else:
            coords = []
            [coords.extend((y, x)) for x, y in self.aoi_geom.coords[0]]
            geom = 'poly:"{}"'.format(' '.join(map(str, coords)))

        if self.feature_selection:
            nodes,ways,relations = self.feature_selection.overpass_filter()
            args.update({
                'nodes':"\n".join(['node(' + geom + ')' + f + ';' for f in nodes]),
                'ways':"\n".join(['way(' + geom + ')' + f + ';'  for f in ways]),
                'relations':"\n".join(['relation(' + geom + ')' + f + ';' for f in relations]),
            })

            query = OSM_XML.filter_template.safe_substitute(args)
        else:
            args.update({
                'geom': geom,
            })
            query = OSM_XML.basic_template.safe_substitute(args)

        # set up required paths
        LOG.debug("Query started at: %s" % datetime.now())
        LOG.debug("Query: %s", query)
        req = requests.post('{}interpreter'.format(self.url), data=query, stream=True, timeout=20*60)
        CHUNK = 1024 * 1024 * 5  # 5MB chunks
        with open(self.output_xml, 'wb') as fd:
            for chunk in req.iter_content(CHUNK):
                fd.write(chunk)
        self.raise_if_bad()
        LOG.debug('Query finished at %s' % datetime.now())
        LOG.debug('Wrote overpass query results to: %s' % self.output_xml)

    @property
    def results(self):
        return [Artifact([self.output_xml],OSM_XML.name)]

    @property
    def is_complete(self):
        return os.path.isfile(self.output_xml)
