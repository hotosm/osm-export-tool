import yaml

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

    def filter(self,theme):
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
