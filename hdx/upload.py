import os


countries = ['GIN', 'LBR', 'MLI', 'SEN', 'SLE']
themes = ['buildings','roads','waterways','points_of_interest','admin_boundaries']

for country in ['GIN']:
    for theme in themes:
        dataset = Dataset()
        name = 'bdon-hot-openstreetmap-' + country.lower() + '-' + theme
        dataset['name'] = name
        dataset['title'] = country + ' ' + theme + ' (OpenStreetMap Export)'
        dataset['private'] = True
        dataset['notes'] = "Test note."
        dataset['dataset_source'] = 'OpenStreetMap'
        dataset['dataset_date'] = '03/01/2017'
        dataset['owner_org'] = '225b9f7d-e7cb-4156-96a6-44c9c58d31e3'
        dataset['license_id'] = 'hdx-odc-odbl'
        dataset['methodology'] = 'Other'
        dataset['methodology_other'] = 'OpenStreetMap extract'
        dataset['data_update_frequency'] = '7'
        dataset['subnational'] = '1'
        dataset.add_country_location(country)

        resources = []

        for table in ['points','lines','polygons']:
            resources.append({
                'name': table,
                'format': 'zipped shapefile',  
                'url': '{0}/{1}/{2}.zip'.format(os.environ['HDX_TEST_BUCKET'],country,table),
                'description': "description for " + table
            })

        dataset.add_update_resources(resources)

        d = Dataset.read_from_hdx(name)
        if d:
            dataset.update_in_hdx()
        else:
            dataset.create_in_hdx()


