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

class TestManager(unittest.TestCase):

    def test_map_names_to_formats(self):
        m = map_names_to_formats([
            "osm_xml",
            "osm_pbf",
            "geopackage",
            "shp",
            "kml",
            "garmin_img",
            "osmand_obf"
            ])
        self.assertEqual(m,[
            OSM_XML,
            OSM_PBF,
            Geopackage,
            Shapefile,
            KML,
            GarminIMG,
            OsmAndOBF
        ])
