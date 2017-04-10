# -*- coding: utf-8 -*-
from __future__ import with_statement

import argparse
import logging
import os
import shutil
import subprocess
import zipfile
import sqlite3
from string import Template

LOG = logging.getLogger(__name__)
exts = ['.shp','.dbf','.prj','.shx','.cpg']

class ThematicSHP(object):
    """
    Exports thematic GPKG to shapefiles
    """
    name = 'theme_shp'
    description = 'Esri SHP (Thematic Schema)'

    def __init__(self, input_gpkg, output_dir, feature_selection,aoi_geom,per_theme=True):
        self.gpkg = input_gpkg
        self.feature_selection = feature_selection
        self.output_dir = output_dir + "/"
        self.per_theme = per_theme
        self.aoi_geom = aoi_geom

    def run(self):
        for table in self.feature_selection.tables:
            subprocess.check_call('ogr2ogr -f "ESRI Shapefile" {0}/{1}.shp {2} -lco ENCODING=UTF-8 -sql "select * from {1};"'.format(
                self.output_dir,
                table,
                self.gpkg),shell=True,executable='/bin/bash')

        if self.per_theme:
            for table in self.feature_selection.tables:
                with zipfile.ZipFile(self.output_dir + table + ".zip",'w',zipfile.ZIP_DEFLATED) as z:
                    z.writestr("boundary.geojson",self.aoi_geom.json)
                    for e in exts:
                        if os.path.isfile(self.output_dir+table+e):
                            z.write(self.output_dir + table + e,table + e)
        else:
            with zipfile.ZipFile(self.output_dir + "thematic_shps.zip",'w',zipfile.ZIP_DEFLATED) as z:
                z.writestr("boundary.geojson",self.aoi_geom.json)
                for table in self.feature_selection.tables:
                    for e in exts:
                        if os.path.isfile(self.output_dir+table+e):
                            z.write(self.output_dir + table + e,table + e)

        LOG.debug("cleanup")
        for e in exts:
            for table in self.feature_selection.tables:
                if os.path.isfile(self.output_dir+table+e):
                    os.remove(self.output_dir + table + e)

    @property
    def is_complete(self):
        return False
    
    @property
    def results(self):
        return [self.output_dir + table + ".zip" for table in self.feature_selection.tables]


