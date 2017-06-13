import types from '../actions/actionTypes';
import initialState from './initialState';

export function drawerMenuReducer(state = initialState.drawerOpen, action) {
    switch(action.type) {
        case types.OPEN_DRAWER:
            return true;
        case types.CLOSE_DRAWER:
            return false;
        default:
            return state;
    }
}

export function exportModeReducer(state = initialState.mode, action) {
    switch(action.type) {
        case types.SET_MODE:
            return action.mode;
        default:
            return state;
    }
}

export function exportInfoReducer(state = initialState.exportInfo, action) {
  switch(action.type) {
    case types.RECEIVED_EXPORT:
      return action.job
  }
  return state;
}

export function exportAoiInfoReducer(state = initialState.aoiInfo, action) {
    switch(action.type) {
        case types.UPDATE_AOI_INFO:
            return {
                geojson: action.geojson,
                geomType: action.geomType,
                title: action.title,
                description: action.description,
            };
        case types.CLEAR_AOI_INFO:
            return {
                geojson: {},
                geomType: null,
                title: null,
                description: null,
            };
        default:
            return state;
    }
}


export function getProvidersReducer(state = initialState.providers, action ) {
    switch (action.type) {
        case types.GETTING_PROVIDERS:
            return  []
        case types.PROVIDERS_RECEIVED:
            return action.providers
        default:
            return state
    }
}
