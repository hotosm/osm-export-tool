import os
import json
import subprocess
import zipfile
from shapely.geometry import shape, mapping
from feature_selection import FeatureSelection

from hdx.data.dataset import Dataset
from hdx.configuration import Configuration

MARKDOWN = '''
Shapefiles of [OpenStreetMap](http://www.openstreetmap.org) features in {region}.

The shapefiles include all OpenStreetMap features matching:

{criteria}

The shapefiles include these attributes:

{columns}

This dataset is one of many [OpenStreetMap exports on HDX](https://data.humdata.org/dataset?tags=openstreetmap).
See the [Humanitarian OpenStreetMap Team](http://hotosm.org/) website for more information.
'''

class HDXExportSet(object):
    """
    An HDXExportSet is a set of remote resources (HDX datasets)
    corresponding to a feature selection and area of interest.
    This is a plain old python object that can be used independent of the web application.
    """

    def __init__(self,dataset_prefix,name,extent,feature_selection,country_codes=[]):
        # raise exceptions on invalid feature selections, extents.
        # it's not the job of this class to validate those!
        assert extent['type'] in ['Polygon','MultiPolygon']
        self._extent = extent
        self._feature_selection = feature_selection
        self._dataset_prefix = dataset_prefix
        self._name = name
        self._country_codes = country_codes
        self._datasets = None

    @property
    def country_codes(self):
        return self._country_codes

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

    @property
    def datasets(self): 
        if self._datasets:
            return self._datasets

        self._datasets = []
        for theme in self._feature_selection.themes:
            dataset = Dataset()
            name = self._dataset_prefix + "_" + theme
            dataset['name'] = name
            dataset['title'] = self._name + ' ' + theme + ' (OpenStreetMap Export)'
            dataset['private'] = True
            dataset['notes'] = self.hdx_note(theme)
            dataset['dataset_source'] = 'OpenStreetMap'
            dataset['dataset_date'] = '03/01/2017'
            dataset['owner_org'] = '225b9f7d-e7cb-4156-96a6-44c9c58d31e3'
            dataset['license_id'] = 'hdx-odc-odbl'
            dataset['methodology'] = 'Other'
            dataset['methodology_other'] = 'OpenStreetMap extract'
            dataset['data_update_frequency'] = '7'
            dataset['subnational'] = '1'
            for country_code in self._country_codes:
                dataset.add_country_location(country_code)
            self._datasets.append(dataset)
        return self._datasets


    def hdx_note(self,theme):
        columns = []
        for key in self._feature_selection.key_selections(theme):
            columns.append("- [{0}](http://wiki.openstreetmap.org/wiki/Key:{0})".format(key))
        columns = "\n".join(columns)
        return MARKDOWN.format(
            region = self._name,
            criteria = self._feature_selection.filter_clause(theme),
            columns = columns
        )

    def sync_datasets(self):
        for dataset in self.datasets:
            exists = Dataset.read_from_hdx(dataset['name'])
            if exists:
                dataset.update_in_hdx()
            else:
                dataset.create_in_hdx()

    # will get to these later...

    def zip_resources(self,stage_root):
        stage_dir = stage_root + h.base_slug + '/'
        sqlite = stage_dir + h.base_slug + ".sqlite"
        for table in self._feature_selection.tables:
            subprocess.check_call('ogr2ogr -f "ESRI Shapefile" {0}{1}/{2}.shp {3} -lco ENCODING=UTF-8 -sql "select * from {2};"'.format(stage_root,self.base_slug,table,sqlite),shell=True,executable='/bin/bash')
            exts = ['.shp','.dbf','.prj','.shx','.cpg']
            with zipfile.ZipFile(stage_dir + h.base_slug + "_" + table + ".zip",'w',zipfile.ZIP_DEFLATED) as z:
                for e in exts:
                    z.write(stage_dir + table + e,table + e)
            for e in exts:
                os.remove(stage_dir + table + e)

    def sync_resources(self):
            resources = []
            for geom_type in self._feature_selection.geom_types(theme):
                resource_name = theme + '_' + geom_type # DRY me up
                resources.append({
                    'name': resource_name,
                    'format': 'zipped shapefile',  
                    'url': '{0}/{1}.zip'.format(os.environ['HDX_TEST_BUCKET'],self._base_slug + '_' + resource_name),
                    'description': "ESRI Shapefile of " + geom_type
                })
            dataset.add_update_resources(resources)


if __name__ == "__main__":
    f_s = FeatureSelection(open('hdx_exports/example_preset.yml').read())
    extent = json.loads(open('hdx_exports/adm0/GIN_adm0.geojson').read())
    h = HDXExportSet('hotosm_guinea','Guinea',extent,f_s,country_codes=['GIN'])
    #h.zip_resources("../stage/")
    Configuration.create(hdx_site='prod',hdx_key=os.environ['HDX_API_KEY'])
    h.sync_datasets()
