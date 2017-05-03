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

TEST_FEATURE_SELECTION = FeatureSelection("""
buildings:
  types:
    - polygons
  select:
    - name
    - building
    - building_levels
    - building_materials
    - addr_housenumber
    - addr_street
    - addr_city
    - office
  where: building IS NOT NULL

roads:
  types:
    - lines
    - polygons
  select:
    - name
    - highway
    - surface
    - smoothness
    - width
    - lanes
    - oneway
    - bridge
    - layer
  where: highway IS NOT NULL
""")

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
        aoi_geom = Polygon.from_bbox((-17.417,14.754,-17.395,14.772))
        fmts = [Geopackage,Shapefile,KML]
        r = RunManager(
            fmts,
            aoi_geom,
            TEST_FEATURE_SELECTION,
            stage_dir,
            per_theme=True,
            overpass_api_url=os.environ.get('OVERPASS_API_URL')
        )
        r.run()

        target_dir = stage_dir + "target"
        os.mkdir(target_dir)
        zipper = Zipper("test",stage_dir,target_dir,aoi_geom,TEST_FEATURE_SELECTION)
        for f in fmts:
            zipper.run(r.results[f].results)
        z = zipper.zipped_resources
        self.assertEqual(len([x for x in z if x.format_name == 'kml']),3)
        self.assertEqual(len([x for x in z if x.format_name == 'shp']),2) # no road polygons present
        self.assertEqual(len([x for x in z if x.format_name == 'geopackage']),2)
        self.assertEqual(z[0].parts[0],"test_roads_gpkg.zip")


    def test_export_img(self):
        self.setup_stage_dir()
        aoi_geom = Polygon.from_bbox((-17.417,14.754,-17.395,14.772))
        r = RunManager(
            [GarminIMG],
            aoi_geom,
            TEST_FEATURE_SELECTION,
            stage_dir,
            garmin_splitter=os.environ.get("GARMIN_SPLITTER",'/opt/splitter/splitter.jar'),
            garmin_mkgmap=os.environ.get("GARMIN_MKGMAP",'/opt/mkgmap/mkgmap.jar')
        )
        r.run()
        target_dir = stage_dir + "target"
        os.mkdir(target_dir)
        zipper = Zipper("test",stage_dir,target_dir,aoi_geom,TEST_FEATURE_SELECTION)
        zipper.run(r.results[GarminIMG].results)
        z = zipper.zipped_resources
        self.assertEqual(len(z),1) # one themeless img

