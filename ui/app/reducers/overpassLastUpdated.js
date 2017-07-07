import types from "../actions";

export default function overpassLastUpdated(state = null, action) {
  switch (action.type) {
    case types.RECEIVED_OVERPASS_TIMESTAMP:
      return action.lastUpdated;

    default:
      return state;
  }
}
