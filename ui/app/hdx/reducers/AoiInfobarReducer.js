import types from '../actions/actionTypes';
import initialState from './initialState';

export function zoomToSelectionReducer(state = initialState.zoomToSelection, action) {
    switch(action.type) {
        case types.CLICK_ZOOM_TO_SELECTION:
            return Object.assign({}, state, {click: !state.click});
        default:
            return state;
    }
}

export function resetMapReducer(state = initialState.resetMap, action) {
    switch(action.type) {
        case types.CLICK_RESET_MAP:
            return Object.assign({}, state, {click: !state.click});
        default:
            return state;
    }
}
