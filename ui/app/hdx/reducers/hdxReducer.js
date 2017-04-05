import types from '../actions/actionTypes';
import initialState from './initialState';

export function getHdxReducer (state = initialState.hdx, { error, exportRegion, exportRegions, id, type }) {
  switch (type) {
    case types.FETCHING_EXPORT_REGION:
      return {
        ...state,
        fetching: true,
        fetched: false,
        exportRegion: null,
        error: null
      };

    case types.FETCHING_EXPORT_REGIONS:
      return {
        ...state,
        fetching: true,
        fetched: false,
        exportRegions: [],
        error: null
      };

    case types.RECEIVED_EXPORT_REGION:
      return {
        ...state,
        fetching: false,
        fetched: true,
        exportRegion,
        error: null
      };

    case types.RECEIVED_EXPORT_REGIONS:
      return {
        ...state,
        fetching: false,
        fetched: true,
        exportRegions,
        error: null
      };

    case types.FETCH_EXPORT_REGIONS_ERROR:
      return {
        ...state,
        fetching: false,
        fetched: false,
        exportRegions: [],
        id,
        error
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
