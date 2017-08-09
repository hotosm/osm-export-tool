import types from "../actions";

const initialState = {
  loading: false
};

export default function status(state = initialState, { type }) {
  switch (type) {
    case types.FETCHING_EXPORT_LIST:
      return {
        ...state,
        loading: true
      };

    case types.RECEIVED_EXPORT_LIST:
      return {
        ...state,
        loading: false
      };

    default:
      return state;
  }
}
