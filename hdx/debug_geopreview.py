import os
import json

from hdx.data.dataset import Dataset
from hdx.configuration import Configuration

Configuration.create(hdx_site='prod')
base_slug = 'hotosm_guinea'
theme = 'admin_boundaries'
dataset = Dataset()
name = base_slug + "_" + theme
dataset['name'] = name
dataset['title'] = 'Guinea admin boundaries (OpenStreetMap Export)'
dataset['private'] = True
dataset['dataset_source'] = 'OpenStreetMap'
dataset['dataset_date'] = '03/01/2017'
dataset['owner_org'] = '225b9f7d-e7cb-4156-96a6-44c9c58d31e3'
dataset['license_id'] = 'hdx-odc-odbl'
dataset['methodology'] = 'Other'
dataset['methodology_other'] = 'OpenStreetMap extract'
dataset['data_update_frequency'] = '7'

resources = []
for geom_type in ['points','lines','polygons']:
    resource_name = theme + '_' + geom_type
    resources.append({
        'name': resource_name,
        'format': 'zipped shapefile',  
        'url': 'https://s3.us-east-2.amazonaws.com/bdon-osm2hdx/hotosm_guinea_admin_boundaries.zip',
        'description': "ESRI Shapefile of " + geom_type
    })
dataset.add_update_resources(resources)
d = Dataset.read_from_hdx(name)
if d:
    dataset.update_in_hdx()
else:
    dataset.create_in_hdx()



