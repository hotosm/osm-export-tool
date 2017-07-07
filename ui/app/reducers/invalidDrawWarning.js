import types from "../actions";

export default function invalidDrawWarning(state = "", action) {
  switch (action.type) {
    case types.SHOW_INVALID_DRAW_WARNING:
      return action.msg;

    case types.HIDE_INVALID_DRAW_WARNING:
      return "";

    default:
      return state;
  }
}
