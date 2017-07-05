import types from '../actions/actionTypes';
import initialState from './initialState';

export function exportModeReducer (state = initialState.mode, action) {
  switch (action.type) {
    case types.SET_MODE:
      return action.mode;
    default:
      return state;
  }
}

export function exportInfoReducer (state = initialState.exportInfo, action) {
  switch (action.type) {
    case types.RECEIVED_EXPORT:
      return {
        ...action.job,
        simplified_geom: {
          ...action.job.simplified_geom,
          id: action.job.simplified_geom.id || Math.random()
        }
      };
  }
  return state;
}

export function exportRunsReducer (state = initialState.exportRuns, action) {
  switch (action.type) {
    case types.RECEIVED_RUNS:
      return action.runs;
  }
  return state;
}

export function jobListReducer (state = initialState.jobs, action) {
  switch (action.type) {
    case types.RECEIVED_EXPORT_LIST:
      return {
        ...state,
        nextPageUrl: action.response.next,
        prevPageUrl: action.response.previous,
        items: action.response.results,
        total: action.response.count
      };
  }
  return state;
}

export function overpassTimestampReducer (
  state = initialState.overpassLastUpdated,
  action
) {
  switch (action.type) {
    case types.RECEIVED_OVERPASS_TIMESTAMP:
      return action.lastUpdated;
  }
  return state;
}

export function exportAoiInfoReducer (state = initialState.aoiInfo, action) {
  switch (action.type) {
    case types.UPDATE_AOI_INFO:
      return {
        geojson: action.geojson,
        geomType: action.geomType,
        title: action.title,
        description: action.description
      };
    case types.CLEAR_AOI_INFO:
      return {
        geojson: null,
        geomType: null,
        title: null,
        description: null
      };
    default:
      return state;
  }
}
