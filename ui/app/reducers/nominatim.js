import types from "../actions";

const initialState = {
  fetching: false,
  fetched: false,
  nominatim: {},
  error: null
};

export default function nominatim(state = initialState, action) {
  switch (action.type) {
    case types.FETCHING_NOMINATIM:
      return { fetching: true, fetched: false, nominatim: [], error: null };

    case types.RECEIVED_NOMINATIM:
      return {
        fetching: false,
        fetched: true,
        nominatim: action.nominatim,
        error: null
      };

    case types.FETCH_NOMINATIM_ERROR:
      return {
        fetching: false,
        fetched: false,
        nominatim: [],
        error: action.error
      };

    default:
      return state;
  }
}
