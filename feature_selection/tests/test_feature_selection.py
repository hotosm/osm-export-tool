# -*- coding: utf-8 -*-

import unittest
import yaml
from feature_selection.feature_selection import FeatureSelection, SQLValidator

class TestSQLValidator(unittest.TestCase):
    def test_empty_sql(self):
        s = SQLValidator("")
        self.assertFalse(s.valid)

    def test_minimal(self):
        s = SQLValidator("name IS NOT NULL")
        self.assertTrue(s.valid)

    def test_malicious_sql(self):
        s = SQLValidator("name IS NOT NULL; drop table planet_osm_polygon;")
        self.assertFalse(s.valid)
        s = SQLValidator("(drop table planet_osm_polygon)")
        self.assertFalse(s.valid)
        s = SQLValidator("(drop table planet_osm_polygon) > 0") # integer?
        self.assertFalse(s.valid)

    def test_conditions(self):
        s = SQLValidator("name = 'water'")
        self.assertTrue(s.valid)
        s = SQLValidator("name IS NOT NULL AND admin:level = '4'")
        self.assertTrue(s.valid)
        s = SQLValidator("(name IS NOT NULL AND admin:level = '4')")
        self.assertTrue(s.valid)
        s = SQLValidator("name in ('water','park')")
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
                - name
                - waterway
        buildings:
            types:
                - lines
                - polygons
            select:
                - name
                - building
            where: building IS NOT NULL
        '''
        f = FeatureSelection(y)
        self.assertEquals(f.themes,['buildings','waterways'])
        self.assertEquals(f.geom_types('waterways'),['lines','polygons'])
        self.assertEquals(f.key_selections('waterways'),['name','waterway'])
        self.assertEquals(f.filter_clause('waterways'),'1') # SELECT WHERE 1
        self.assertEquals(f.key_union, ['building','name','waterway'])
        self.assertEquals(f.filter_clause('buildings'),'building IS NOT NULL')

    def test_sqls(self):
        y = '''
        buildings:
            types:
                - points
                - polygons
            select:
                - name
                - addr:housenumber
        '''
        f = FeatureSelection(y)
        create_sqls, index_sqls = f.sqls
        self.assertEquals(create_sqls[0],"CREATE TABLE buildings_points AS SELECT geom,osm_id,'name','addr:housenumber' FROM planet_osm_point WHERE (1)")
        self.assertEquals(create_sqls[1],"CREATE TABLE buildings_polygons AS SELECT geom,osm_id,osm_way_id,'name','addr:housenumber' FROM planet_osm_polygon WHERE (1)")


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
        self.assertEqual(f.geom_types('all'),['points','lines','polygons'])

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

    def test_dash_spacing_yaml(self):
        # top level is a list and not a dict
        y = '''
        all: 
          select:
            -name
        '''
        f = FeatureSelection(y)
        self.assertFalse(f.valid)

    def test_no_select_yaml(self):
        # top level is a list and not a dict
        y = '''
        all: 
          -select:
            - name
        '''
        f = FeatureSelection(y)
        self.assertFalse(f.valid)
        self.assertEqual(f.errors[0],"Each theme must have a 'select' key")

    # refer to https://taginfo.openstreetmap.org/keys
    def test_valid_invalid_key_yaml(self):
        y = '''
        all: 
          select:
            - has space
            - has_underscore
            - has:colon
            - UPPERCASE
        '''
        f = FeatureSelection(y)
        self.assertTrue(f.valid)
        y = '''
        all: 
          select:
            - na?me
        '''
        f = FeatureSelection(y)
        self.assertFalse(f.valid)
        self.assertEqual(f.errors[0],"Invalid OSM key: na?me")
        y = '''
        all: 
          select:
            -
        '''
        f = FeatureSelection(y)
        self.assertFalse(f.valid)
        self.assertEqual(f.errors[0],"Missing OSM key")


