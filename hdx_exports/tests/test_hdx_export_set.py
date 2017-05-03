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

SINGLE_THEME_NOTE = """
OpenStreetMap exports for use in GIS applications.

This theme includes all OpenStreetMap features in this area.

Features have these attributes:

- [name](http://wiki.openstreetmap.org/wiki/Key:name)

This dataset is one of many [OpenStreetMap exports on
HDX](/dataset?tags=openstreetmap).
See the [Humanitarian OpenStreetMap Team](http://hotosm.org/) website for more
information.
"""

SINGLE_FILTER_NOTE = """
OpenStreetMap exports for use in GIS applications.

This theme includes all OpenStreetMap features in this area matching:

    highway IS NOT NULL

Features have these attributes:

- [name](http://wiki.openstreetmap.org/wiki/Key:name)

This dataset is one of many [OpenStreetMap exports on
HDX](/dataset?tags=openstreetmap).
See the [Humanitarian OpenStreetMap Team](http://hotosm.org/) website for more
information.
"""

class TestHDXExportSet(unittest.TestCase):
    maxDiff = None

    def test_minimal_export_set(self):

        h = HDXExportSet(
            dataset_prefix="hot_dakar",
            name="Dakar Urban Area",
            extent=DAKAR_GEOJSON_POLYGON,
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
            feature_selection=BASIC_FEATURE_SELECTION
            )


    def test_single_theme_note(self):
        yaml = '''
        all:
            select:
                - name
        '''
        h = HDXExportSet(
            dataset_prefix="hot_dakar",
            name="Dakar Urban Area",
            extent=DAKAR_GEOJSON_POLYGON,
            feature_selection=FeatureSelection(yaml)
        )
        self.assertMultiLineEqual(h.hdx_note('all'),SINGLE_THEME_NOTE)

    def test_filtered_note(self):
        yaml = '''
        some:
            select:
                - name
            where: highway IS NOT NULL
        '''
        h = HDXExportSet(
            dataset_prefix="hot_dakar",
            name="Dakar Urban Area",
            extent=DAKAR_GEOJSON_POLYGON,
            feature_selection=FeatureSelection(yaml)
        )
        self.assertMultiLineEqual(h.hdx_note('some'),SINGLE_FILTER_NOTE)
