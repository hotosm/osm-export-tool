import types from "../../actions/actionTypes";
import initialState from "../initialState";

export function invalidDrawWarningReducer(
  state = initialState.invalidDrawWarning,
  action
) {
  switch (action.type) {
    case types.SHOW_INVALID_DRAW_WARNING:
      return action.msg;
    case types.HIDE_INVALID_DRAW_WARNING:
      return "";
    default:
      return state;
  }
}
