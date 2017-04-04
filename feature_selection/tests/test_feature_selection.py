# -*- coding: utf-8 -*-

import unittest
import yaml
from feature_selection.feature_selection import FeatureSelection, SQLValidator

class TestSQLValidator(unittest.TestCase):
    def test_empty_sql(self):
        s = SQLValidator("")
        self.assertFalse(s.valid)

    @unittest.skip("temporarily disabled")
    def test_minimal(self):
        s = SQLValidator("name IS NOT NULL")
        self.assertTrue(s.valid)

    @unittest.skip("temporarily disabled")
    def test_malicious_sql(self):
        s = SQLValidator("name IS NOT NULL; drop table planet_osm_polygon;")
        self.assertFalse(s.valid)
        s = SQLValidator("(drop table planet_osm_polygon)")
        self.assertFalse(s.valid)
        s = SQLValidator("(drop table planet_osm_polygon) > 0") # integer?
        self.assertFalse(s.valid)

    def test_conditions(self):
        s = SQLValidator("natural = 'water'")
        self.assertTrue(s.valid)
        s = SQLValidator("admin IS NOT NULL AND admin:level = '4'")
        self.assertTrue(s.valid)
        s = SQLValidator("(admin IS NOT NULL AND admin:level = '4')")
        self.assertTrue(s.valid)
        s = SQLValidator("natural in ('water','park')")
        self.assertTrue(s.valid)
        s = SQLValidator("height > 0")
        self.assertTrue(s.valid)

class TestFeatureSelection(unittest.TestCase):

    def test_empty_feature_selection(self):
        y = '''
        '''
        f = FeatureSelection(y)
        self.assertFalse(f.valid)

    def test_key_union_and_filters(self):
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
            where: building IS NOT NULL
        '''
        f = FeatureSelection(y)
        self.assertEquals(f.themes,['buildings','waterways'])
        self.assertEquals(f.geom_types('waterways'),['lines','polygons'])
        self.assertEquals(f.key_selections('waterways'),['osm_id','name','waterway'])
        self.assertEquals(f.filter_clause('waterways'),'1') # SELECT WHERE 1
        self.assertEquals(f.key_union, ['building','name','osm_id','waterway'])
        self.assertEquals(f.filter_clause('buildings'),'building IS NOT NULL')

    @unittest.skip("temporarily disabled")
    def test_sqls(self):
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
        print f.sqls

    def test_unsafe_yaml(self):
        y = '''
        !!python/object:feature_selection.feature_selection.FeatureSelection
        a: 0
        '''
        f = FeatureSelection(y)
        self.assertFalse(f.valid)
        self.assertEqual(1,len(f.errors))

    def test_malformed_yaml(self):
        # if it's not a valid YAML document
        # TODO: errors for if yaml indentation is incorrect
        y = '''
        all
            select:
                - name
        '''
        f = FeatureSelection(y)
        self.assertFalse(f.valid)

    def test_minimal_yaml(self):
        # the shortest valid feature selection
        y = '''
        all: 
            select:
                - name
        '''
        f = FeatureSelection(y)
        self.assertTrue(f.valid)

    def test_unspecified_yaml(self):
        # top level is a list and not a dict
        y = '''
        - all: 
            select:
                - name
        '''
        f = FeatureSelection(y)
        self.assertFalse(f.valid)
        self.assertEqual(f.errors[0],"YAML must be dict, not list")
