import os
from datetime import datetime
import django.utils.text
from hdx.data.dataset import Dataset
from osm_export_tool.mapping import Mapping

FILTER_CRITERIA = """
This theme includes all OpenStreetMap features in this area matching:

{criteria}
"""

MARKDOWN = """
OpenStreetMap exports for use in GIS applications.
{filter_str}
Features may have these attributes:

{columns}

This dataset is one of many [OpenStreetMap exports on
HDX](https://data.humdata.org/organization/hot).
See the [Humanitarian OpenStreetMap Team](http://hotosm.org/) website for more
information.
"""

def slugify(str):
    s = django.utils.text.slugify(str)
    return s.replace('-','_')

def sync_datasets(datasets,update_dataset_date=False):
    for dataset in datasets:
        exists = Dataset.read_from_hdx(dataset['name'])
        if exists:
            if update_dataset_date:
                dataset.set_dataset_date_from_datetime(datetime.now())
            dataset.update_in_hdx()
        else:
            dataset.set_dataset_date_from_datetime(datetime.now())
            dataset.create_in_hdx(allow_no_resources=True)

def sync_region(region,files=[],public_dir=''):
    export_set = HDXExportSet(
        Mapping(region.feature_selection),
        region.dataset_prefix,
        region.name,
        region.extra_notes
    )
    datasets = export_set.datasets(
        region.is_private,
        region.subnational,
        region.update_frequency,
        region.locations,
        files,
        public_dir
    )
    sync_datasets(datasets,len(files) > 0)

class HDXExportSet(object):
    def __init__(self,mapping,dataset_prefix,name,extra_notes=''):
        self._dataset_prefix = dataset_prefix
        self._extra_notes = extra_notes + '\n' if extra_notes else ''
        self._mapping = mapping
        self._name = name

    # used in the serializer
    def dataset_links(self,hdx_prefix_url):
        return [{
            'name': '{}_{}'.format(self._dataset_prefix, slugify(theme.name)),
            'url': '{}dataset/{}_{}'.format(
                hdx_prefix_url, self._dataset_prefix, slugify(theme.name)),
        } for theme in self._mapping.themes]

    def hdx_note(self, theme):
        columns = []
        for key in theme.keys:
            columns.append('- [{0}](http://wiki.openstreetmap.org/wiki/Key:{0})'.format(key))
        columns = '\n'.join(columns)

        criteria = theme.matcher.to_sql()
        filter_str = FILTER_CRITERIA.format(criteria=criteria)

        return self._extra_notes + MARKDOWN.format(
                region=self._name,
                columns=columns,
                filter_str=filter_str
            )

    def datasets(self,is_private,subnational,data_update_frequency,locations,files,public_dir):
        HDX_FORMATS = {
            'geojson':'GeoJSON',
            'shp': 'SHP',
            'geopackage': 'Geopackage',
            'garmin_img': 'Garmin IMG',
            'kml': 'KML'
        }

        HDX_DESCRIPTIONS = {
            'geojson': 'Geographic JavaScript Object Notation',
            'shp':'ESRI Shapefile',
            'geopackage':'Geopackage, SQLite compatible',
            'garmin_img':'.IMG for Garmin GPS Devices (All OSM layers for area)',
            'kml':'Google Earth .KML'
        }

        d = []
        updated_by_script = f'HOT Export Tool ({datetime.now().strftime("%Y-%m-%dT%H:%M:%S")})'
        for theme in self._mapping.themes:
            dataset = Dataset()
            dataset['owner_org'] = '225b9f7d-e7cb-4156-96a6-44c9c58d31e3'
            dataset['maintainer'] = '6a0688ce-8521-46e2-8edd-8e26c0851ebd'
            dataset['dataset_source'] = 'OpenStreetMap contributors'
            dataset['methodology'] = 'Other'
            dataset['methodology_other'] = 'Volunteered geographic information'
            dataset['license_id'] = 'hdx-odc-odbl'
            dataset['updated_by_script'] = updated_by_script
            dataset['groups'] = []

            dataset['name'] = '{0}_{1}'.format(self._dataset_prefix, slugify(theme.name))
            dataset['title'] = '{0} {1} (OpenStreetMap Export)'.format(self._name, theme.name)
            dataset['notes'] = self.hdx_note(theme)

            dataset['private'] = is_private
            dataset['subnational'] = str(int(subnational))
            dataset['data_update_frequency'] = str(data_update_frequency)

            if 'hdx' in theme.extra:
                if 'caveats' in theme.extra['hdx']:
                    dataset['caveats'] = theme.extra['hdx']['caveats']
                if 'tags' in theme.extra['hdx']:
                    tags = [tag.strip() for tag in theme.extra['hdx']['tags'].split(',')]
                    dataset.add_tags(tags)

            for location in locations:
                # warning: this makes a network call
                dataset.add_other_location(location)

            resources = []
            for f in files:
                if isinstance(f, dict): # it is coming from galaxy
                    if f['theme'] == theme.name:
                        file_name = f['file_name'] # only one part: the zip file
                        resources.append({
                        'name': file_name, 
                        'format': HDX_FORMATS[f['output_name']],
                        'description': HDX_DESCRIPTIONS[f['output_name']],
                        'url': f['download_url']
                        }) 
                else: 
                    if 'theme' not in f.extra or f.extra['theme'] == theme.name:
                        file_name = os.path.basename(f.parts[0]) # only one part: the zip file
                        resources.append({
                        'name': file_name, 
                        'format': HDX_FORMATS[f.output_name],
                        'description': HDX_DESCRIPTIONS[f.output_name],
                        'url': os.path.join(public_dir,file_name)
                        })
            # stable sort, but put shapefiles first for Geopreview to pick up correctly
            resources.sort(key=lambda x: 0 if x['format'] == 'zipped shapefile' else 1)
            dataset.add_update_resources(resources)
            d.append(dataset)
        return d



