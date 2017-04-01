# -*- coding: utf-8 -*-

import json
import unittest
from hdx_exports.hdx_export_set import HDXExportSet
from feature_selection.feature_selection import FeatureSelection
from django.contrib.gis.geos import GEOSGeometry

from hdx.data.hdxobject import HDXError

DAKAR_GEOJSON_POLYGON = json.dumps({
        "type": "Polygon",
        "coordinates": [
          [
            [-17.465,14.719],
            [-17.442,14.719],
            [-17.442,14.741],
            [-17.465,14.741],
            [-17.465,14.719]
          ]
        ]
      })

DAKAR_GEOJSON_MULTIPOLYGON = json.dumps({
        "type": "MultiPolygon",
        "coordinates": [[
          [
            [-17.465,14.719],
            [-17.442,14.719],
            [-17.442,14.741],
            [-17.465,14.741],
            [-17.465,14.719]
          ]]
        ]
      })

yaml = '''
buildings:
    types:
        - polygons
    select:
        - building
    where: building is not null

waterways:
    types:
        - lines
        - polygons
    select:
        - natural
    where: natural in ('waterway')
'''
BASIC_FEATURE_SELECTION = FeatureSelection(yaml)

class TestHDXExportSet(unittest.TestCase):

    def test_minimal_export_set(self):

        h = HDXExportSet(
            "hot_dakar",
            "Dakar Urban Area",
            DAKAR_GEOJSON_POLYGON, # or multipolygon. maybe this should be Shapely geom instead of dict?
            BASIC_FEATURE_SELECTION
        )
        self.assertEquals([],h.country_codes)
        datasets = h.datasets
        self.assertEquals(len(datasets),2)
        self.assertEquals(datasets[0]['name'],'hot_dakar_buildings')

    def test_extent_not_polygon_or_multipolygon(self):
        with self.assertRaises(AssertionError):
            h = HDXExportSet(
                "hot_dakar",
                "Dakar Urban Area",
                GEOSGeometry("{'type':'LineString','coordinates':[]}"),
                BASIC_FEATURE_SELECTION 
            )

    def test_invalid_country_codes(self):
        h = HDXExportSet(
            "hot_dakar",
            "Dakar Urban Area",
            DAKAR_GEOJSON_POLYGON,
            BASIC_FEATURE_SELECTION,
            country_codes=['XXX']
        )
        with self.assertRaises(HDXError):
            h.datasets
    
