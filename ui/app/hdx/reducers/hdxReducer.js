import types from '../actions/actionTypes';
import initialState from './initialState';

export function getHdxReducer (state = initialState.hdx, { error, exportRegion, exportRegions, id, statusCode, type }) {
  switch (type) {
    case types.FETCHING_EXPORT_REGION:
      return {
        ...state,
        fetching: true,
        fetched: false,
        error: null,
        status: `Fetching export region ${id}...`
      };

    case types.FETCHING_EXPORT_REGIONS:
      return {
        ...state,
        fetching: true,
        fetched: false,
        error: null,
        status: 'Fetching export regions...'
      };

    case types.RECEIVED_EXPORT_REGION:
      return {
        ...state,
        fetching: false,
        fetched: true,
        exportRegions: {
          ...state.exportRegions,
          [id]: exportRegion
        },
        error: null,
        status: `Export region ${id} loaded.`
      };

    case types.RECEIVED_EXPORT_REGIONS:
      return {
        ...state,
        fetching: false,
        fetched: true,
        exportRegions,
        error: null,
        status: `Export regions loaded.`
      };

    case types.FETCH_EXPORT_REGIONS_ERROR:
      return {
        ...state,
        fetching: false,
        fetched: false,
        exportRegions: {},
        status: `Fetching export regions failed: ${error.message}`,
        id,
        error,
        statusCode
      };

    case types.STARTING_EXPORT_REGION_RUN:
      return {
        ...state,
        status: 'Starting export region run...',
        id
      };

    case types.EXPORT_REGION_RUN_STARTED:
      return {
        ...state,
        status: 'Export region run started.',
        id
      };

    case types.EXPORT_REGION_RUN_ERROR:
      return {
        ...state,
        status: `Export region run failed: ${error.message}`,
        id,
        error,
        statusCode
      };

    case types.STARTING_EXPORT_REGION_DELETE:
      return {
        ...state,
        status: 'Starting to delete export region...',
        id
      };

    case types.EXPORT_REGION_DELETED:
      exportRegions = {
        ...state.exportRegions
      };
      delete exportRegions[id];

      return {
        ...state,
        status: 'Export region deleted.',
        exportRegions,
        id
      };

    case types.DELETE_EXPORT_REGION_ERROR:
      return {
        ...state,
        status: `Export region deletion failed: ${error.message}`,
        id,
        error,
        statusCode
      };

    case types.ZOOM_TO_EXPORT_REGION:
      return {
        ...state,
        selectedExportRegion: id
      };

    default:
      return state;
  }
}
