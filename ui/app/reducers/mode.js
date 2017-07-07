import types from "../actions";

export default function mode(state = "DRAW_NORMAL", { mode, type }) {
  switch (type) {
    case types.SET_MODE:
      return mode;

    default:
      return state;
  }
}
