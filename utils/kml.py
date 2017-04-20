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
    description = 'Google Earth KML'

    def __init__(self, input_gpkg, output_dir,feature_selection,per_theme=False):
        """
        Initialize the GPKGToKml utility.

        Args:
            gpkg: the GeoPackage to convert
            kmlfile: where to write the kml output
            debug: turn debugging on / off
        """
        self.input_gpkg = input_gpkg
        self.output_dir = output_dir
        self.feature_selection = feature_selection
        self.per_theme = per_theme

    def run(self):
        """
        Convert GeoPackage to kml.
        """
        if self.is_complete:
            LOG.debug("Skipping KML, files exist")

        for table in self.feature_selection.tables:
            subprocess.check_call('ogr2ogr -f "KML" {0}/{1}.kml {2} -sql "select * from {1};"'.format(
                self.output_dir,
                table,
                self.input_gpkg),shell=True,executable='/bin/bash')

    @property
    def is_complete(self):
        return all(os.path.isfile(result) for result in self.results)

    @property
    def results(self):
        return [os.path.join(self.output_dir,table,".kml") for table in self.feature_selection.tables]
