# -*- coding: utf-8 -*-

import unittest
from utils import FORMAT_NAMES, map_names_to_formats
from utils.osm_xml import OSM_XML
from utils.osm_pbf import OSM_PBF
from utils.kml import KML
from utils.geopackage import Geopackage
from utils.shp import Shapefile
from utils.garmin_img import GarminIMG
from utils.osmand_obf import OsmAndOBF
from utils.manager import RunManager, Zipper
from feature_selection.feature_selection import FeatureSelection
import os
import logging
import glob
import shutil
from django.contrib.gis.geos import GEOSGeometry, Polygon

xml = os.path.dirname(os.path.realpath(__file__)) + '/files/export.osm'
stage_dir = os.path.dirname(os.path.realpath(__file__)) + '/stage/'
logging.basicConfig(level=logging.DEBUG)

class TestManager(unittest.TestCase):

    def setup_stage_dir(self):
        try:
            shutil.rmtree(stage_dir)
        except:
            pass
        os.mkdir(stage_dir)
        shutil.copy(xml,stage_dir+"export.osm")

    def test_export_shp(self):
        self.setup_stage_dir()
        feature_selection = FeatureSelection.example('hdx')
        aoi_geom = Polygon.from_bbox((-17.417,14.754,-17.395,14.772))
        fmts = [Geopackage,Shapefile,KML]
        r = RunManager(
            fmts,
            aoi_geom,
            feature_selection,
            stage_dir,
            per_theme=True,
            overpass_api_url=os.environ.get('OVERPASS_API_URL')
        )
        r.run()

        target_dir = stage_dir + "target"
        os.mkdir(target_dir)
        zipper = Zipper("test",stage_dir,target_dir,aoi_geom)
        for f in fmts:
            zipper.run(r.results[f].results,f.name)

        z = zipper.resources_by_theme()
        roads = z['roads']
        self.assertEqual(roads[0],('test_roads_gpkg.zip', 'geopackage'))
        self.assertEqual(roads[1],('test_roads_lines_shp.zip', 'shp'))

