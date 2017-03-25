import types from '../actions/actionTypes';
import initialState from './initialState';

export function invalidDrawWarningReducer(state = initialState.showInvalidDrawWarning, action) {
    switch(action.type) {
        case types.SHOW_INVALID_DRAW_WARNING:
            return action.showInvalidDrawWarning;
        case types.HIDE_INVALID_DRAW_WARNING:
            return action.showInvalidDrawWarning;
        default:
            return state;
    }
}
