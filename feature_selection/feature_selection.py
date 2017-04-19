import re
import yaml
from yaml.constructor import ConstructorError
from yaml.scanner import ScannerError
from sql import SQLValidator

CREATE_TEMPLATE = 'CREATE TABLE {0} AS SELECT geom,{1} FROM {2} WHERE ({3})'
INDEX_TEMPLATE = """
INSERT INTO gpkg_contents (table_name, data_type,identifier,srs_id) VALUES ('{0}','features','{0}','4326');
INSERT INTO gpkg_geometry_columns VALUES ('{0}', 'geom', '{1}', '4326', '0', '0');
UPDATE '{0}' SET geom=GeomFromGPB(geom);
SELECT gpkgAddSpatialIndex('{0}', 'geom');
UPDATE '{0}' SET geom=AsGPB(geom);
"""

WKT_TYPE_MAP = {
    'points':'POINT',
    'lines':'MULTILINESTRING',
    'polygons':'MULTIPOLYGON'
}

OSM_ID_TAGS = {
    'points':['osm_id'],
    'lines':['osm_id'],
    'polygons':['osm_id','osm_way_id']
}

OGR2OGR_TABLENAMES = {
    'points':'planet_osm_point',
    'lines':'planet_osm_line',
    'polygons':'planet_osm_polygon'
}


# FeatureSelection seralizes as YAML.
# It describes a set of tables (themes)
# to create in a Spatialite database.
class FeatureSelection(object):
    def __init__(self,raw_doc):
        self._raw_doc = raw_doc
        self._doc = None
        self._errors = []
        self.keys_from_sql = set()

    @property
    def doc(self):

        def validate_schema(loaded_doc):
            if not isinstance(loaded_doc,dict):
                self._errors.append("YAML must be dict, not list")
                return False
            for theme, theme_dict in loaded_doc.iteritems():
                if 'select' not in theme_dict:
                    self._errors.append("Each theme must have a 'select' key")
                    return False
                for key in theme_dict['select']:
                    if not key:
                        self._errors.append("Missing OSM key")
                        return False
                    if not re.match("[a-zA-Z0-9 _\:]+$",key):
                        self._errors.append("Invalid OSM key: {0}".format(key))
                        return False
                if not isinstance(theme_dict['select'],list):
                    self._errors.append("'select' children must be list elements (e.g. '- amenity')")
                    return False
                if 'where' in theme_dict:
                    s = SQLValidator(theme_dict['where'])
                    if not s.valid:
                        self._errors.append("SQL WHERE Invalid: " + ';'.join(s.errors))
                        return False

                    # also add the keys to keys_from_sql
                    for k in s.column_names:
                        self.keys_from_sql.add(k)

            return True

        if self._doc:
            return self._doc
        try:
            loaded_doc = yaml.safe_load(self._raw_doc)
            if validate_schema(loaded_doc):
                self._doc = loaded_doc
                return self._doc
        except (ConstructorError,ScannerError) as e:
            line = e.problem_mark.line
            column = e.problem_mark.column
            #print e.problem_mark.buffer
            #print e.problem
            self._errors.append(e.problem)
            # add exceptions
            #self._valid = (self._yaml != None)


    @property
    def valid(self):
        return self.doc != None

    @property
    def errors(self):
        return self._errors

    @property
    def themes(self):
        return self.doc.keys()

    def geom_types(self,theme):
        if 'types' in self.doc[theme]:
            return self.doc[theme]['types']
        return ['points','lines','polygons']

    def key_selections(self,theme):
        return self.doc[theme]['select']

    def filter_clause(self,theme):
        theme = self.doc[theme]
        if 'where' in theme:
            return theme['where']
        return '1'

    def __str__(self):
        return str(self.doc)

    @property
    def key_union(self):
        s = set()
        for t in self.themes:
            for key in self.key_selections(t):
                s.add(key)
        for key in self.keys_from_sql:
            s.add(key)
        return sorted(list(s))

    @property
    def tables(self):
        retval = []
        for theme in self.themes:
            for geom_type in self.geom_types(theme):
                retval.append(theme + '_' + geom_type)
        return retval

    @property
    def sqls(self):
        create_sqls = []
        index_sqls = []
        for theme in self.themes:
            key_selections = ['"{0}"'.format(key) for key in self.key_selections(theme)]
            filter_clause = self.filter_clause(theme)
            for geom_type in self.geom_types(theme):
                dst_tablename = theme + '_' + geom_type
                src_tablename = OGR2OGR_TABLENAMES[geom_type]
                create_sqls.append(CREATE_TEMPLATE.format(
                    dst_tablename, 
                    ','.join(OSM_ID_TAGS[geom_type] + key_selections), 
                    src_tablename, 
                    filter_clause
                ))
                index_sqls.append(INDEX_TEMPLATE.format(
                    dst_tablename,
                    WKT_TYPE_MAP[geom_type]
                ))
        return create_sqls, index_sqls
