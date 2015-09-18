/*
 * Configuration object.
 * Urls for API endpoints.
 */

Config = {}

// region / region mask endpoints (GeoJSON)
Config.REGIONS_URL = '/api/regions.json'
Config.REGION_MASK_URL = '/api/maskregions.json'

// job / run / format / configurations endpoints
Config.JOBS_URL = '/api/jobs'
Config.RUNS_URL = '/api/runs'
Config.RERUN_URL = '/api/rerun?job_uid='
Config.EXPORT_FORMATS_URL = '/api/formats.json'
Config.CONFIGURATION_URL = '/api/configurations'


// datamodel endpoints
Config.HDM_TAGS_URL = '/api/hdm-data-model?format=json'
Config.OSM_TAGS_URL = '/api/osm-data-model?format=json'

// nominatum
Config.NOMINATIM_SEARCH_URL = 'http://nominatim.openstreetmap.org/search'
Config.MAPQUEST_SEARCH_URL = 'http://open.mapquestapi.com/nominatim/v1/search'

// error pages
Config.CREATE_ERROR_URL = '/error'


