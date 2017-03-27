
import actions from './actionTypes';

export function hideInvalidDrawWarning() {
    return {
        type: actions.HIDE_INVALID_DRAW_WARNING,
        showInvalidDrawWarning: false
    }
}

export function showInvalidDrawWarning() {
    return {
        type: actions.SHOW_INVALID_DRAW_WARNING,
        showInvalidDrawWarning: true
    }
}
