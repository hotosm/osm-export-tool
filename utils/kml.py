# -*- coding: utf-8 -*-
from __future__ import with_statement

import argparse
import logging
import os
import subprocess
import zipfile
from string import Template
from utils.artifact import Artifact
from feature_selection.feature_selection import slugify

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
        return False

    # return a dict of themes -> lists, with each list entry being a file path of created artifact
    # or a list of resources that should be together
    @property
    def results(self):
        results_list = []
        one_zipfile_contents = []
        for theme in self.feature_selection.themes:
            for geom_type in self.feature_selection.geom_types(theme):
                basename = os.path.join(self.output_dir,slugify(theme)+"_"+geom_type) + ".kml"
                if self.per_theme:
                    results_list.append(Artifact([basename],KML.name,theme=theme))
                else:
                    one_zipfile_contents.append(basename)

        if not self.per_theme:
            results_list.append(Artifact(one_zipfile_contents,KML.name,basename="kml"))
        return results_list
