# -*- coding: utf-8 -*-

import logging
import os
from string import Template
from subprocess import PIPE, Popen

from utils.artifact import Artifact
from utils.osm_xml import OSM_XML

LOG = logging.getLogger(__name__)


class InvalidOsmXmlException(Exception):
    pass


class UnfilteredPBF(object):
    name = 'full_pbf'
    description = 'Unfiltered OSM PBF'
    cmd = Template('osmconvert $osm --out-pbf >$pbf')

    def __init__(self, aoi_geom, output_pbf, url):
        self.aoi_geom = aoi_geom
        self.output_pbf = output_pbf
        self.url = url

    def run(self):
        if self.is_complete:
            LOG.debug("Skipping UnfilteredPBF, file exists")
            return

        osm_xml = "{}.xml".format(self.output_pbf)

        osm_xml_task = OSM_XML(self.aoi_geom, osm_xml, url=self.url)
        osm_xml_task.run()

        convert_cmd = self.cmd.safe_substitute({
            'osm': osm_xml,
            'pbf': self.output_pbf
        })

        LOG.debug('Running: %s' % convert_cmd)

        p = Popen(convert_cmd, shell=True, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()

        if stderr:
            raise InvalidOsmXmlException(stderr)

        LOG.debug('Osmconvert complete')

    @property
    def results(self):
        return [Artifact([self.output_pbf], UnfilteredPBF.name)]

    @property
    def is_complete(self):
        return os.path.isfile(self.output_pbf)
