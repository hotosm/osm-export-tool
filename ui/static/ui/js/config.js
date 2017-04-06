/*
 * Configuration object.
 * Urls for API endpoints.
 */

Config = {}

// job / run / format / configurations endpoints
Config.JOBS_URL = '/api/jobs'
Config.RUNS_URL = '/api/runs'
Config.EXPORT_FORMATS_URL = '/api/formats.json'
Config.CONFIGURATION_URL = '/api/configurations'
Config.SCHEDULED_EXPORTS_URL = '/api/scheduled_exports'

// datamodel endpoints
Config.HDM_TAGS_URL = '/api/hdm-data-model?format=json'
Config.OSM_TAGS_URL = '/api/osm-data-model?format=json'

// nominatum
Config.NOMINATIM_SEARCH_URL = 'http://nominatim.openstreetmap.org/search'
Config.MAPQUEST_SEARCH_URL = 'http://open.mapquestapi.com/nominatim/v1/search'

// geonames
Config.GEONAMES_SEARCH_URL = 'http://api.geonames.org/searchJSON'

// error pages
Config.CREATE_ERROR_URL = '/error'
Config.UPDATE_BROWSER_URL = '/update'
