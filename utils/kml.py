# -*- coding: utf-8 -*-
from __future__ import with_statement

import argparse
import logging
import os
import subprocess
import zipfile
from string import Template

LOG = logging.getLogger(__name__)


class KML(object):
    """
    Thin wrapper around ogr2ogr to convert GPKG to KML.
    """
    name = 'kml'
    description = 'Google Earth KMZ'

    def __init__(self, input_gpkg, output_file):
        """
        Initialize the GPKGToKml utility.

        Args:
            gpkg: the GeoPackage to convert
            kmlfile: where to write the kml output
            debug: turn debugging on / off
        """
        self.input_gpkg = input_gpkg
        self.output_file = output_file
        self.cmd = Template("ogr2ogr -f 'KML' $kmlfile $gpkg")

    def run(self):
        """
        Convert GeoPackage to kml.
        """
        if self.is_complete:
            LOG.debug("Skipping KML, file exists")
            return

        if self.output_file.endswith("kmz"):
            kml_name = self.output_file[:-1] + 'l'
        else:
            kml_name = self.output_file
        
        print kml_name

        convert_cmd = self.cmd.safe_substitute({'kmlfile': kml_name,
                                                'gpkg': self.input_gpkg})
        LOG.debug('Running: %s' % convert_cmd)
        subprocess.check_call(convert_cmd, shell=True, executable='/bin/bash')
        if self.output_file.endswith("kmz"):
            with zipfile.ZipFile(self.output_file,'w',zipfile.ZIP_DEFLATED) as z:
                z.write(kml_name,os.path.basename(kml_name))
            LOG.debug('Zipped KML: {0}'.format(self.output_file))

        return self.output_file

    @property
    def is_complete(self):
        return os.path.isfile(self.output_file)

    @property
    def results(self):
        return [self.output_file]
