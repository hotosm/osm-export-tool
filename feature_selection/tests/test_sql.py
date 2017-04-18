# -*- coding: utf-8 -*-

import unittest
from feature_selection.sql import SQLValidator

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
        s = SQLValidator("height > +20")
        self.assertTrue(s.valid)
        s = SQLValidator("height > -20")
        self.assertTrue(s.valid)

    def test_not_null(self):
        s = SQLValidator("height IS NOT NULL")
        self.assertTrue(s.valid)
        s = SQLValidator("height IS NULL")
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

