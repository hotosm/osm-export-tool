import sqlparse
from sqlparse.tokens import Token
import yaml
from yaml.constructor import ConstructorError
from yaml.scanner import ScannerError

#CREATE_TEMPLATE = 'CREATE TABLE {0} AS SELECT Geometry,osm_id,{1} FROM {2} WHERE ({3}) AND ST_Contains(GeomFromText(?),Geometry);'
CREATE_TEMPLATE = 'CREATE TABLE {0} AS SELECT geom,osm_id,{1} FROM {2} WHERE ({3})'
#INDEX_TEMPLATE = "SELECT RecoverGeometryColumn('{0}', 'GEOMETRY', 4326, '{1}', 'XY')"
# TODO dont hardcode date
INDEX_TEMPLATE = """
INSERT INTO gpkg_contents VALUES ('{0}', 'features', '{0}', '', '2017-04-08T01:35:16.576Z', null, null, null, null, '4326');
INSERT INTO gpkg_geometry_columns VALUES ('{0}', 'geom', '{1}', '4326', '0', '0');
UPDATE '{0}' SET geom=GeomFromGPB(geom);
SELECT gpkgAddSpatialIndex('{0}', 'geom');
UPDATE '{0}' SET geom=AsGPB(geom);
"""


WKT_TYPE_MAP = {
    'points':'POINT',
    'lines':'LINESTRING',
    'polygons':'MULTIPOLYGON'
}

OGR2OGR_TABLENAMES = {
    'points':'planet_osm_point',
    'lines':'planet_osm_line',
    'polygons':'planet_osm_polygon'
}

class SQLValidator(object):
    def __init__(self,raw_sql):
        self._raw_sql = raw_sql
        self._sql = None
        self._errors = []

    @property
    def sql(self):
        if self._sql:
            return self._sql
        if not self._raw_sql:
            self._errors.append(["SQL clause is empty"])
            return None

        parsed = sqlparse.parse(self._raw_sql)

        def is_valid_identifier(value):
            print value
            return True

        
        def is_whitelisted(token):
            print token
            print token.ttype
            if isinstance(token,sqlparse.sql.Identifier):
                return is_valid_identifier(token.value)
            if isinstance(token,sqlparse.sql.IdentifierList):
                x = True
                for v in token.tokens:
                    x = (x and is_valid_identifier(v))
                    return x
            if isinstance(token,sqlparse.sql.Comparison):
                left = is_whitelisted(token.left)
                right = is_whitelisted(token.right)
                return (left and right)
            if isinstance(token,sqlparse.sql.Parenthesis):
                x = True
                for t in token.tokens:
                    x = (x and is_whitelisted(t))
                return x
            if token.ttype in [
                Token.Keyword,
                Token.Text.Whitespace,
                Token.Operator.Comparison,
                Token.Literal.String.Single,
                Token.Literal.Number.Integer,
                Token.Punctuation
                ]:
                return True
            return False

        for statement in parsed:
            for token in statement.tokens:
                if not is_whitelisted(token):
                    self._errors.append("SQL Invalid")
                    return None
        self._sql = self._raw_sql
        return self._sql


    @property
    def valid(self):
        return not (self.sql == None)

    @property
    def errors(self):
        return ""

class InvalidFeatureSelectionException(Exception):
    pass

class ValidationErrorRepr(object):
    def __init__(self,error):
        self._error = error

    def to_dict(self):
        pass

# FeatureSelection seralizes as YAML.
# It describes a set of tables (themes)
# to create in a Spatialite database.
class FeatureSelection(object):
    def __init__(self,raw_doc):
        self._raw_doc = raw_doc
        self._doc = None
        self._errors = []

    @property
    def doc(self):
        def validate_schema(loaded_doc):
            if not isinstance(loaded_doc,dict):
                self._errors.append("YAML must be dict, not list")
                return False
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

    @property
    def key_union(self):
        s = set()
        for t in self.themes:
            for key in self.key_selections(t):
                s.add(key)
        return sorted(list(s))

    @property
    def tables(self):
        retval = []
        for theme in self.themes:
            for geom_type in self.geom_types(theme):
                retval.append(theme + '_' + geom_type)
        return retval

    # TODO make me secure against injection
    @property
    def sqls(self):
        create_sqls = []
        index_sqls = []
        for theme in self.themes:
            for geom_type in self.geom_types(theme):
                dst_tablename = theme + '_' + geom_type
                key_selections = ','.join(self.key_selections(theme))
                src_tablename = OGR2OGR_TABLENAMES[geom_type]
                filter_clause = self.filter_clause(theme)
                create_sqls.append(CREATE_TEMPLATE.format(
                    dst_tablename, 
                    key_selections, 
                    src_tablename, 
                    filter_clause
                ))
                index_sqls.append(INDEX_TEMPLATE.format(
                    dst_tablename,
                    WKT_TYPE_MAP[geom_type]
                ))
        return create_sqls, index_sqls
