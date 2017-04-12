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

    def __init__(self, input_gpkg, feature_selection,stage_dir,per_theme=True):
        self.gpkg = input_gpkg
        self.feature_selection = feature_selection
        self.stage_dir = stage_dir

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

        # this creates per-theme GPKGs
        WKT_TYPE_MAP = {
            'points':'POINT',
            'lines':'MULTILINESTRING',
            'polygons':'MULTIPOLYGON'
        }
        for theme in self.feature_selection.themes:
            conn = sqlite3.connect(self.stage_dir + theme + ".gpkg")
            conn.enable_load_extension(True)
            cur = conn.cursor()
            cur.execute("attach database ? as 'geopackage'",(self.gpkg,))
            cur.execute("create table gpkg_spatial_ref_sys as select * from geopackage.gpkg_spatial_ref_sys")
            cur.execute("create table gpkg_contents as select * from geopackage.gpkg_contents where 0")
            cur.execute("create table gpkg_geometry_columns as select * from geopackage.gpkg_geometry_columns where 0")
            for geom_type in self.feature_selection.geom_types(theme):
                table_name = theme + "_" + geom_type
                cur.execute("create table {0} as select * from geopackage.{0}".format(table_name))
                cur.execute("INSERT INTO gpkg_contents VALUES ('{0}', 'features', '{0}', '', '2017-04-08T01:35:16.576Z', null, null, null, null, '4326')".format(table_name))
                cur.execute("INSERT INTO gpkg_geometry_columns VALUES ('{0}', 'geom', '{1}', '4326', '0', '0')".format(table_name,WKT_TYPE_MAP[geom_type]))
            conn.commit()
            conn.close()

    @property
    def is_complete(self):
        return False
    
    @property
    def results(self):
        return [self.stage_dir + theme + ".gpkg" for theme in self.feature_selection.themes]

