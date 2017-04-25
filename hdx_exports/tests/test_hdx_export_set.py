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
            dataset_prefix="hot_dakar",
            name="Dakar Urban Area",
            extent=DAKAR_GEOJSON_POLYGON, # or multipolygon. maybe this should be Shapely geom instead of dict?
            feature_selection=BASIC_FEATURE_SELECTION
        )
        datasets = h.datasets
        self.assertEquals(len(datasets),2)
        self.assertEquals(datasets['buildings']['name'],'hot_dakar_buildings')
        self.assertEquals(datasets['waterways']['name'],'hot_dakar_waterways')

    def test_extent_not_polygon_or_multipolygon(self):
        with self.assertRaises(AssertionError):
            h = HDXExportSet(
            dataset_prefix="hot_dakar",
            name="Dakar Urban Area",
            extent=GEOSGeometry("{'type':'LineString','coordinates':[]}"),
            feature_selection=BASIC_FEATURE_SELECTION,
            locations=['XXX']
            )

    def test_invalid_country_codes(self):
        h = HDXExportSet(
            dataset_prefix="hot_dakar",
            name="Dakar Urban Area",
            extent=DAKAR_GEOJSON_POLYGON, # or multipolygon. maybe this should be Shapely geom instead of dict?
            feature_selection=BASIC_FEATURE_SELECTION,
            locations=['XXX']
        )
        with self.assertRaises(HDXError):
            h.datasets
    
