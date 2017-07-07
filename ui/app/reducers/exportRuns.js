import types from "../actions";

export default function exportRuns(state = [], action) {
  switch (action.type) {
    case types.RECEIVED_RUNS:
      return action.runs;

    default:
      return state;
  }
}
