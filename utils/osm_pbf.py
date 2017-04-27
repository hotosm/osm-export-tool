# -*- coding: utf-8 -*-

import logging
import os
import subprocess
from string import Template
from artifact import Artifact

LOG = logging.getLogger(__name__)

class OSM_PBF(object):
    name = 'osm_pbf'
    description = 'OSM PBF'
    cmd = Template('osmconvert $osm --out-pbf >$pbf')

    def __init__(self,input_xml,output_pbf):
        """
        Initialize the OSMToPBF utility.

        Args:
            osm: the raw osm file to convert
            pbffile: the location of the pbf output file
        """
        self.input_xml = input_xml
        self.output_pbf = output_pbf

    def run(self):
        if self.is_complete:
            LOG.debug("Skipping OSM_PBF, file exists")
            return
        convert_cmd = OSM_PBF.cmd.safe_substitute({'osm': self.input_xml, 'pbf':self.output_pbf})
        LOG.debug('Running: %s' % convert_cmd)
        subprocess.check_call(convert_cmd, shell=True, executable='/bin/bash', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        LOG.debug('Osmconvert complete')

    @property
    def results(self):
        return [Artifact([self.output_pbf],OSM_PBF.name)]

    @property
    def is_complete(self):
        return os.path.isfile(self.output_pbf)
