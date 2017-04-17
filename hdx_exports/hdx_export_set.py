# noqa

from datetime import datetime
import os
import subprocess
import zipfile

from feature_selection.feature_selection import FeatureSelection
from hdx.data.dataset import Dataset
from hdx.data.galleryitem import GalleryItem
from hdx.configuration import Configuration

from django.contrib.gis.geos import GEOSGeometry

Configuration.create(
    hdx_site='demo',
    hdx_key=os.environ.get('HDX_API_KEY', None),
)

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
            tags = []
            if 'hdx_tags' in self._feature_selection.doc[theme]:
                tags = map(lambda tag: tag.strip(),
                           self._feature_selection.doc[theme]['hdx_tags'].split(','))
            title = self._feature_selection.doc[theme].get(
                'hdx_name',
                '{} {} (OpenStreetMap Export)'.format(self._name, theme)
            )
            caveats = self._feature_selection.doc[theme].get('hdx_caveats', '')

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
            # TODO this appends locations rather than resetting them
            dataset['groups'] = []
            dataset.add_country_locations(self._locations)
            # TODO probably appends tags rather than replacing them
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
        for dataset in self.datasets.values():
            exists = Dataset.read_from_hdx(dataset['name'])
            if exists:
                dataset.update_in_hdx()
            else:
                dataset.create_in_hdx()

    # will get to these later...

    def zip_resources(self, stage_root, job_name): # noqa
        stage_dir = stage_root + job_name + '/'
        sqlite = stage_dir + job_name + '.sqlite'
        for table in self._feature_selection.tables:
            subprocess.check_call('ogr2ogr -f "ESRI Shapefile" {0}{1}/{2}.shp {3} -lco ENCODING=UTF-8 -sql "select * from {2};"'.format(stage_root, job_name, table, sqlite), shell=True, executable='/bin/bash')
            exts = ['.shp', '.dbf', '.prj', '.shx', '.cpg']
            with zipfile.ZipFile(stage_dir + job_name + '_' + table + '.zip', 'w', zipfile.ZIP_DEFLATED) as z:
                for e in exts:
                    z.write(stage_dir + table + e, table + e)

            for e in exts:
                os.remove(stage_dir + table + e)


if __name__ == '__main__':
    import logging
    logging.basicConfig()

    Configuration.create(
        hdx_site='demo',
        hdx_key=os.environ.get('HDX_API_KEY', None),
    )
    f_s = FeatureSelection(open('hdx_exports/example_preset.yml').read())
    extent = open('hdx_exports/adm0/GIN_adm0.geojson').read()
    h = HDXExportSet(
        'hotosm_guinea',
        'Guinea',
        extent,
        f_s,
        country_codes=['GIN'],
    )
    # h.zip_resources("../stage/","hotosm_guinea")
    # h.sync_resources("../stage/","hotosm_guinea")
    h.sync_datasets()
