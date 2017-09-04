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
    default_template = Template('[maxsize:$maxsize][timeout:$timeout];(node($bbox);<;>>;>;);out meta;')

    def __init__(self, aoi_geom, output_xml,
                url='http://overpass-api.de/api/',
                overpass_max_size=4294967296,
                timeout=1600):
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
        # extract all nodes / ways and relations within the bounding box
        # see: http://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_QL

        # dump out all osm data for the specified bounding box

    def raise_if_bad(self):
        with open(self.output_xml,'rb') as fd:
            sample = fd.readlines(8)
            if len(sample) == 7:
                raise EmptyOsmXmlException
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
        extent = self.aoi_geom.extent  # (w,s,e,n)
        west = max(extent[0],-180)
        south = max(extent[1],-90)
        east = min(extent[2],180)
        north = min(extent[3],90)
        
        # overpass needs extents in order (s,w,n,e) and from -180 to 180, -90 to 90

        query = OSM_XML.default_template.safe_substitute(
            {'maxsize': self.overpass_max_size, 'timeout': self.timeout, 'bbox':'{1},{0},{3},{2}'.format(west,south,east,north)}
        )
        # set up required paths
        LOG.debug("Query started at: %s" % datetime.now())
        req = requests.post('{}interpreter'.format(self.url), data=query, stream=True)
        CHUNK = 1024 * 1024 * 5  # 5MB chunks
        with open(self.output_xml, 'wb') as fd:
            for chunk in req.iter_content(CHUNK):
                fd.write(chunk)
        self.raise_if_empty()
        LOG.debug('Query finished at %s' % datetime.now())
        LOG.debug('Wrote overpass query results to: %s' % self.output_xml)

    @property
    def results(self):
        return [Artifact([self.output_xml],OSM_XML.name)]

    @property
    def is_complete(self):
        return os.path.isfile(self.output_xml)

