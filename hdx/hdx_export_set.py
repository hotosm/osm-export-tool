import json
from shapely.geometry import shape, mapping
from feature_selection import FeatureSelection

class HDXExportSet(object):

    def __init__(self,extent_path,feature_selection,base_slug):
        self._extent_path = extent_path
        self._feature_selection = feature_selection
        self._base_slug = base_slug

    @property
    def bounds(self):
        return self.clipping_polygon.bounds

    @property
    def clipping_polygon(self):
        f = open(self._extent_path)
        features = json.loads(f.read())['features']
        assert len(features) == 1
        theshape = shape(features[0]['geometry'])
        theshape = theshape.buffer(0.01)
        theshape = theshape.simplify(0.01)
        return theshape
        #with open('temp.geojson','w') as out:
        #    out.write(json.dumps(mapping(theshape)))
        

    # has one hdx dataset per theme.
    @property
    def hdx_datasets(self): 
        return self._feature_selection.themes

if __name__ == "__main__":
    f_s = FeatureSelection(open('hdx/example_preset.yml').read())
    h = HDXExportSet('hdx/adm0/SLE_adm0.geojson',f_s,'hot-openstreetmap-senegal')
    print h.hdx_datasets
