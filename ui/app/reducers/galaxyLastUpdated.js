import types from "../actions";

export default function galaxyLastUpdated(state = null, action) {
  switch (action.type) {
    case types.RECEIVED_GALAXY_TIMESTAMP:
      return action.lastUpdated;

    default:
      return state;
  }
}
