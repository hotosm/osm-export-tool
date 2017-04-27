# noqa

from datetime import datetime
import logging
import os
import subprocess
import traceback
import zipfile

from feature_selection.feature_selection import FeatureSelection
from hdx.data.dataset import Dataset
from hdx.data.galleryitem import GalleryItem
from hdx.configuration import Configuration
from raven import Client

from django.contrib.gis.geos import GEOSGeometry
from utils.artifact import Artifact

client = Client()

LOG = logging.getLogger(__name__)

MARKDOWN = """
Shapefiles of [OpenStreetMap](http://www.openstreetmap.org) features in
{region}.

The shapefiles include all OpenStreetMap features matching:

{criteria}

The shapefiles include these attributes:

{columns}

This dataset is one of many [OpenStreetMap exports on
HDX](https://data.humdata.org/dataset?tags=openstreetmap).
See the [Humanitarian OpenStreetMap Team](http://hotosm.org/) website for more
information.
"""

class HDXExportSet(object):
    """
    A set of remote resources.

    Each HDXExportSet is a set of remote resources (HDX datasets) corresponding
    to a feature selection and area of interest. This is a plain old python
    object that can be used independent of the web application.
    """

    def __init__(
        self,
        data_update_frequency=None,
        dataset_date=datetime.now(),
        dataset_prefix='',
        extent=None,
        extra_notes='',
        feature_selection=None,
        hostname='exports-staging.hotosm.org',
        is_private=True,
        license='hdx-odc-odbl',
        locations=[],
        name=None,
        subnational=True,
    ): # noqa
        # raise exceptions on invalid feature selections, extents.
        # it's not the job of this class to validate those!
        try:
            assert extent.geom_type in ['Polygon', 'MultiPolygon']
        except Exception:
            extent = GEOSGeometry(extent)

        assert extent.geom_type in ['Polygon', 'MultiPolygon']

        self._data_update_frequency = data_update_frequency
        self._datasets = None
        self._dataset_date = dataset_date
        self._dataset_prefix = dataset_prefix
        self._extent = extent
        self._extra_notes = extra_notes or ''
        self._feature_selection = feature_selection
        self.hostname = hostname
        self.is_private = is_private
        self._license = license
        # NOTE: overrides whatever license is provided
        self._license = 'hdx-odc-odbl'
        self._locations = locations
        self._name = name
        self.subnational = subnational

    @property
    def bounds(self): # noqa
        return self.selection_polygon.bounds

    @property
    def selection_polygon(self): # noqa
        sp = self._extent
        sp = sp.buffer(0.02)
        sp = sp.simplify(0.01)
        return sp

    @property
    def osm_analytics_url(self): # noqa
        bounds = self._extent.extent
        return "http://osm-analytics.org/#/show/bbox:{0},{1},{2},{3}/highways/recency".format(*bounds)

    @property
    def datasets(self): # noqa
        if self._datasets:
            return self._datasets

        self._datasets = {}
        for theme in self._feature_selection.themes:
            dataset = Dataset()
            name = '{}_{}'.format(self._dataset_prefix, theme)
            title = '{} {} (OpenStreetMap Export)'.format(self._name, theme)
            tags = []
            caveats = ''
            if 'hdx' in self._feature_selection.doc[theme]:
                hdx = self._feature_selection.doc[theme]['hdx']
                title = hdx.get('name') or title
                caveats = hdx.get('caveats', caveats)

                if 'tags' in hdx:
                    tags = map(lambda tag: tag.strip(), hdx['tags'].split(','))

            dataset['name'] = name
            dataset['title'] = title
            dataset['caveats'] = caveats
            dataset['private'] = self.is_private
            dataset['notes'] = self.hdx_note(theme)
            dataset['dataset_source'] = 'OpenStreetMap contributors'
            dataset.set_dataset_date_from_datetime(self._dataset_date)
            dataset['owner_org'] = '225b9f7d-e7cb-4156-96a6-44c9c58d31e3'
            dataset['license_id'] = self._license
            dataset['methodology'] = 'Other'
            dataset['methodology_other'] = 'Volunteered geographic information'
            dataset['data_update_frequency'] = str(self._data_update_frequency)
            dataset['subnational'] = str(int(self.subnational))
            dataset['groups'] = []

            # warning: this makes a network call
            [dataset.add_other_location(x) for x in self._locations]
            dataset.add_tags(tags)

            ga = GalleryItem({
                'title': 'OSM Analytics',
                'description': 'View detailed information about OpenStreetMap edit history in this area.',
                'url': self.osm_analytics_url,
                'image_url': 'http://{}/static/ui/images/osm_analytics.png'.format(self.hostname),
                'type': 'Visualization',
            })
            dataset.add_update_galleryitem(ga)

            self._datasets[theme] = dataset
        return self._datasets


    def hdx_note(self, theme): # noqa
        columns = []
        for key in self._feature_selection.key_selections(theme):
            columns.append('- [{0}](http://wiki.openstreetmap.org/wiki/Key:{0})'.format(key))
        columns = '\n'.join(columns)

        return '\n'.join((
            self._extra_notes,
            MARKDOWN.format(
                region=self._name,
                criteria=self._feature_selection.filter_clause(theme),
                columns=columns,
            ),
        ))

    def sync_datasets(self): # noqa
        Configuration.create(
            hdx_site=os.getenv('HDX_SITE', 'demo'),
            hdx_key=os.getenv('HDX_API_KEY'),
        )
        for dataset in self.datasets.values():
            try:
                exists = Dataset.read_from_hdx(dataset['name'])
                if exists:
                    dataset.update_in_hdx()
                else:
                    dataset.create_in_hdx()
            except Exception as e:
                client.captureException()
                LOG.warn(e)
                LOG.warn(traceback.format_exc())

    def sync_resources(self,artifact_list,public_dir):
        Configuration.create(
            hdx_site=os.getenv('HDX_SITE', 'demo'),
            hdx_key=os.getenv('HDX_API_KEY'),
        )
        HDX_FORMATS = {
            'shp':'zipped shapefile',
            'geopackage':'zipped geopackage',
            'garmin_img':'zipped img',
            'osm_pbf':'pbf',
            'kml':'zipped kml'
        }

        for theme in self._feature_selection.themes:
            theme_artifacts = [a for a in artifact_list if (a.theme == theme or a.theme == None)]
            resources = []
            for artifact in theme_artifacts:
                file_name = artifact.parts[0] # only one part: the zip file
                resources.append({
                    'name': file_name,
                    'format': HDX_FORMATS[artifact.format_name],
                    'description': file_name,
                    'url': os.path.join(public_dir,file_name)
                })
            self.datasets[theme].add_update_resources(resources)
        self.sync_datasets()

if __name__ == '__main__':
    import logging
    import json
    import pprint
    import logging
    from hdx.configuration import Configuration
    from hdx.data.dataset import Dataset
    import requests
    import os
    logging.basicConfig()
    f_s = FeatureSelection.example("simple")
    extent = open('adm0/GIN_adm0.geojson').read()
    h = HDXExportSet(
        dataset_prefix='demodata_test',
        name='Guinea',
        extent=extent,
        feature_selection=f_s,
        locations=['GIN']
    )

    h.sync_resources([Artifact(['foo_buildings_polygons.zip'],'geopackage',theme=None)],'http://example.com/')
    pp = pprint.PrettyPrinter(indent=4)
    headers = {
                'Authorization':os.getenv('HDX_API_KEY'),
                'Content-type':'application/json'
            }
    data = json.dumps({'id':'demodata_test'})
    resp = requests.post('https://data.humdata.org/api/action/package_show',headers=headers,data=data)
    for r in resp.json()['result']['resources']:
        pp.pprint(r)
