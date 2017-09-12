import types from "../actions";

const initialState = {
  loading: false
};

export default function status(state = initialState, { type }) {
  switch (type) {
    case types.FETCHING_CONFIGURATIONS:
    case types.FETCHING_EXPORT:
    case types.FETCHING_EXPORT_LIST:
      return {
        ...state,
        loading: true
      };

    case types.RECEIVED_CONFIGURATIONS_LIST:
    case types.FETCHING_EXPORT_FAILED:
    case types.FETCHING_EXPORT_LIST_FAILED:
    case types.RECEIVED_EXPORT:
    case types.RECEIVED_EXPORT_LIST:
      return {
        ...state,
        loading: false
      };

    default:
      return state;
  }
}
