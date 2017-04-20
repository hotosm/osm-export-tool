# -*- coding: utf-8 -*-
from __future__ import with_statement

import argparse
import logging
import os
import shutil
import subprocess
import zipfile
from string import Template

LOG = logging.getLogger(__name__)

exts = ['.shp','.dbf','.prj','.shx','.cpg']

class Shapefile(object):
    """
    Convert a GeoPackage to shapefile.
    """
    name = 'shp'
    description = 'ESRI SHP (OSM Schema)'

    def __init__(self, input_gpkg, output_dir, feature_selection):
        """
        Args:
            gpg: the GeoPackage to convert.
            shapefile: the path to the shapefile output
        """
        self.gpkg = input_gpkg
        self.feature_selection = feature_selection

    def run(self):
        if self.is_complete:
            LOG.debug("Skipping SHP, files exist")
            return

        for table in self.feature_selection.tables:
            subprocess.check_call('ogr2ogr -f "ESRI Shapefile" {0}/{1}.shp {2} -lco ENCODING=UTF-8 -sql "select * from {1};"'.format(
                self.output_dir,
                table,
                self.gpkg),shell=True,executable='/bin/bash')

    @property
    def is_complete(self):
        return all(os.path.isfile(result) for result in results)
    
    @property
    def results(self):
        return [os.path.join(self.output_dir,table,".shp") for table in self.feature_selection.tables]
