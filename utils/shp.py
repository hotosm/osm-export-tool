# -*- coding: utf-8 -*-
from __future__ import with_statement

import argparse
import logging
import os
import shutil
import subprocess
import zipfile
from string import Template
from utils.artifact import Artifact
from feature_selection.feature_selection import slugify

LOG = logging.getLogger(__name__)

exts = ['.shp','.dbf','.prj','.shx','.cpg']

class Shapefile(object):
    """
    Convert a GeoPackage to shapefile.
    """
    name = 'shp'
    description = 'ESRI SHP (OSM Schema)'

    def __init__(self, input_gpkg, output_dir, feature_selection,per_theme=False):
        """
        Args:
            gpg: the GeoPackage to convert.
            shapefile: the path to the shapefile output
        """
        self.gpkg = input_gpkg
        self.feature_selection = feature_selection
        self.output_dir = output_dir
        self.per_theme = per_theme

    def run(self):
        if self.is_complete:
            LOG.debug("Skipping SHP, files exist")
            return
        for table in self.feature_selection.tables:
            subprocess.check_call('ogr2ogr -f "ESRI Shapefile" {0}/{1}.shp {2} -lco ENCODING=UTF-8 -sql "select * from {1};"'.format(
                self.output_dir,
                table,
                self.gpkg),shell=True,executable='/bin/bash',stderr=open(os.devnull))

    # NOTE: if a theme was empty, it won't have a .shp, just a .cpg and .dbf
    # so can't rely on all tables existing to know if this job was done

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
                basename = os.path.join(self.output_dir,slugify(theme)+"_"+geom_type)
                if os.path.isfile(basename+".shp"):
                    shpset = [
                        basename+".shp",
                        basename+".cpg",
                        basename+".dbf",
                        basename+".prj",
                        basename+".shx",
                    ]
                    if self.per_theme:
                        results_list.append(Artifact(shpset,Shapefile.name,theme=theme,basename=basename+".shp"))
                    else:
                        one_zipfile_contents = one_zipfile_contents + shpset
                    
        if not self.per_theme:
            results_list.append(Artifact(one_zipfile_contents,Shapefile.name,basename="shp"))
        return results_list
