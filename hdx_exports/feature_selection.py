import yaml

CREATE_TEMPLATE = 'CREATE TABLE {0} AS SELECT Geometry,osm_id,{1} FROM {2} WHERE ({3}) AND ST_Contains(GeomFromText(?),Geometry);'
INDEX_TEMPLATE = "SELECT RecoverGeometryColumn('{0}', 'GEOMETRY', 4326, '{1}', 'XY')"

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

# FeatureSelection seralizes as YAML.
# It describes a set of tables (themes)
# to create in a Spatialite database.
class FeatureSelection(object):
    def __init__(self,doc):
        self._yaml = yaml.load(doc)
        self._valid = (self._yaml != None)

    @property
    def themes(self):
        return self._yaml.keys()

    @property
    def valid(self):
        return self._valid

    def geom_types(self,theme):
        return self._yaml[theme]['types']

    def key_selections(self,theme):
        return self._yaml[theme]['select']

    def filter_clause(self,theme):
        theme = self._yaml[theme]
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
