/*
 * Configuration object.
 * Urls for API endpoints.
 */

Config = {}

// region / region mask endpoints (GeoJSON)
Config.REGIONS_URL = '/api/regions.json'
Config.REGION_MASK_URL = '/api/maskregions.json'

// job / run / format enpoints
Config.JOBS_URL = '/api/jobs'
Config.RUNS_URL = '/api/runs'
Config.EXPORT_FORMATS_URL = '/api/formats.json'

// datamodel endpoints
Config.HDM_TAGS_URL = '/api/data-model-hdm?format=json'
Config.OSM_TAGS_URL = '/api/data-model-osm?format=json'

// nominatum
Config.NOMINATIM_SEARCH_URL = 'http://nominatim.openstreetmap.org/search'
Config.MAPQUEST_SEARCH_URL = 'http://open.mapquestapi.com/nominatim/v1/search'


