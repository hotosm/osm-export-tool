# -*- coding: utf-8 -*-

import unittest
from feature_selection.sql import SQLValidator, OsmfilterRule

class TestSQLValidator(unittest.TestCase):

    def test_basic(self):
        s = SQLValidator("name = 'a name'")
        self.assertTrue(s.valid)

    def test_identifier_list(self):
        s = SQLValidator("natural in ('water','cliff')")
        self.assertTrue(s.valid)

    #TODO OGR uses text for all things so numerical comparisons will not be correct
    def test_float_value(self):
        s = SQLValidator("height > 20")
        self.assertTrue(s.valid)

    def test_not_null(self):
        s = SQLValidator("height IS NOT NULL")
        self.assertTrue(s.valid)

    def test_and_or(self):
        s = SQLValidator("height IS NOT NULL and height > 20")
        self.assertTrue(s.valid)
        s = SQLValidator("height IS NOT NULL or height > 20")
        self.assertTrue(s.valid)
        s = SQLValidator("height IS NOT NULL or height > 20 and height < 30")
        self.assertTrue(s.valid)

    def test_parens(self):
        s = SQLValidator("(admin IS NOT NULL and level > 4)")
        self.assertTrue(s.valid)
        s = SQLValidator("(admin IS NOT NULL and level > 4) AND height is not null")
        self.assertTrue(s.valid)

    def test_colons_etc(self):
        s = SQLValidator("addr:housenumber IS NOT NULL")
        self.assertFalse(s.valid)
        self.assertEquals(s.errors,['identifier with colon : must be in double quotes.'])
        s = SQLValidator("admin_level IS NOT NULL")
        self.assertTrue(s.valid)
        s = SQLValidator('"addr:housenumber" IS NOT NULL')
        self.assertTrue(s.valid)
        s = SQLValidator('"addr housenumber" IS NOT NULL')
        self.assertTrue(s.valid)

    def test_invalid_sql(self):
        s = SQLValidator("drop table planet_osm_polygon")
        self.assertFalse(s.valid)
        self.assertEquals(s.errors,['SQL could not be parsed.'])
        s = SQLValidator("(drop table planet_osm_polygon)")
        self.assertFalse(s.valid)
        self.assertEquals(s.errors,['SQL could not be parsed.'])
        s = SQLValidator ("")
        self.assertFalse(s.valid)
        self.assertEquals(s.errors,['SQL could not be parsed.'])
        s = SQLValidator("name = 'a name'; blah")
        self.assertFalse(s.valid)
        self.assertEquals(s.errors,['SQL could not be parsed.'])

    def test_column_names(self):
        s = SQLValidator("(admin IS NOT NULL and level > 4) AND height is not null")
        self.assertTrue(s.valid)
        self.assertEquals(s.column_names,['height','level','admin'])


class TestOsmfilterRule(unittest.TestCase):
    def test_basic(self):
        s = OsmfilterRule("name = 'somename'")
        self.assertEqual(s.rule(),"name=somename")
        s = OsmfilterRule("level > 4")
        self.assertEqual(s.rule(),"level>4")

    def test_basic_list(self):
        s = OsmfilterRule("name IN ('val1','val2')")
        self.assertEqual(s.rule(),"name=val1 =val2")

    def test_whitespace(self):
        s = OsmfilterRule("name = 'some value'")
        self.assertEqual(s.rule(),"name=some\\ value")

    def test_notnull(self):
        s = OsmfilterRule("name is not null")
        self.assertEqual(s.rule(),"name=*")

    def test_and_or(self):
        s = OsmfilterRule("name1 = 'foo' or name2 = 'bar'")
        self.assertEqual(s.rule(),"( name1=foo or name2=bar )")
        s = OsmfilterRule("(name1 = 'foo' and name2 = 'bar') or name3 = 'baz'")
        self.assertEqual(s.rule(),"( ( name1=foo and name2=bar ) or name3=baz )")
