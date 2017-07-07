import types from "../actions";

const initialState = {
  nextPageUrl: null,
  prevPageUrl: null,
  total: null,
  items: []
};

export default function configurations(state = initialState, action) {
  switch (action.type) {
    case types.RECEIVED_CONFIGURATIONS_LIST:
      return {
        ...state,
        nextPageUrl: action.response.next,
        prevPageUrl: action.response.previous,
        items: action.response.results,
        total: action.response.count
      };

    default:
      return state;
  }
}
