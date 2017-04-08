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

class ThematicGPKG(object):
    """
    Adds thematic tables tp GPKG
    """
    name = 'theme_gpkg'
    description = 'GeoPackage (Thematic Schema)'

    def __init__(self, input_gpkg, feature_selection,per_theme=True):
        self.gpkg = input_gpkg
        self.feature_selection = feature_selection

    def run(self):
        """
        Add multiple themes to the geopackage.
        """
        conn = sqlite3.connect(self.gpkg)
        conn.enable_load_extension(True)
        cur = conn.cursor()
        cur.execute("select load_extension('mod_spatialite')")
        create_sqls, index_sqls = self.feature_selection.sqls

        for query in create_sqls:
            LOG.debug(query)
            cur.execute(query)
        for query in index_sqls:
            LOG.debug(query)
            cur.executescript(query)
        conn.commit()
        conn.close()

    @property
    def is_complete(self):
        return False
    
    @property
    def results(self):
        return [self.gpkg]

