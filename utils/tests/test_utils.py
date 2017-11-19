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
from utils.aoi_utils import force2d
from django.contrib.gis.geos import GEOSGeometry

class TestUtils(unittest.TestCase):

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

    def test_force_2d(self):
        geojson3d = '{"type":"Polygon","coordinates":[[[-17.279434,14.732386,0],[-17.229996,14.732386,0],[-17.229996,14.779531,0],[-17.279434,14.779531,0],[-17.279434,14.732386,0]]]}}'
        aoi_geom = GEOSGeometry(geojson3d)
        aoi_geom = force2d(aoi_geom)
        self.assertEqual(len(aoi_geom.coords[0][0]),2)
        
        


