import actions from '../actionTypes';

export function hideInvalidDrawWarning() {
    return {
        type: actions.HIDE_INVALID_DRAW_WARNING
    }
}

export function showInvalidDrawWarning(msg) {
    return dispatch => {
        dispatch({
          type: actions.SHOW_INVALID_DRAW_WARNING,
          msg: msg
        })
    }
}
