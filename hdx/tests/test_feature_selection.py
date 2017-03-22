# -*- coding: utf-8 -*-

import unittest
from hdx.feature_selection import FeatureSelection

class TestFeatureSelection(unittest.TestCase):

    def test_empty_feature_selection(self):
        y = '''
        '''
        f = FeatureSelection(y)
        self.assertFalse(f.valid)

    def test_one_theme(self):
        y = '''
        buildings:
            types: 
                - polygons
        '''
        f = FeatureSelection(y)
        self.assertEquals(f.themes,['buildings'])

    def test_theme_geom_types(self):
        y = '''
        waterways:
            types: 
                - lines
                - polygons
        '''
        f = FeatureSelection(y)
        self.assertEquals(f.geom_types('waterways'),['lines','polygons'])

    def test_theme_key_selections(self):
        y = '''
        waterways:
            types: 
                - lines
                - polygons
            select:
                - osm_id
                - name
        '''
        f = FeatureSelection(y)
        self.assertEquals(f.key_selections('waterways'),['osm_id','name'])

    def test_theme_filter(self):
        y = '''
        waterways:
            types: 
                - lines
                - polygons
            select:
                - osm_id
                - name
        '''
        f = FeatureSelection(y)
        self.assertEquals(f.filter('waterways'),'1') # SELECT WHERE 1
        y = '''
        waterways:
            types: 
                - lines
                - polygons
            select:
                - osm_id
                - name
            where: waterway IS NOT NULL
        '''
        f = FeatureSelection(y)
        self.assertEquals(f.filter('waterways'),'waterway IS NOT NULL')

    def test_key_union(self):
        y = '''
        waterways:
            types: 
                - lines
                - polygons
            select:
                - osm_id
                - name
                - waterway
        buildings:
            types:
                - lines
                - polygons
            select:
                - osm_id
                - name
                - building
        '''
        f = FeatureSelection(y)
        self.assertEquals(f.key_union, ['building','name','osm_id','waterway'])
