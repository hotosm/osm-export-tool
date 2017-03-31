import types from '../actions/actionTypes';
import initialState from './initialState';

export function getHdxReducer (state = initialState.hdx, { type, error, exportRegions }) {
  switch (type) {
    case types.FETCHING_EXPORT_REGIONS:
      return {
        fetching: true,
        fetched: false,
        exportRegions: [],
        error: null
      };

    case types.RECEIVED_EXPORT_REGIONS:
      return {
        fetching: false,
        fetched: true,
        exportRegions,
        error: null
      };

    case types.FETCH_EXPORT_REGIONS_ERROR:
      return {
        fetching: false,
        fetched: false,
        exportRegions: [],
        error
      };

    default:
      return state;
  }
}
