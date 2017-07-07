import types from "../actions";

const initialState = {
  items: []
};

export default function configurations(state = initialState, { activePage, itemsPerPage, response, type }) {
  switch (type) {
    case types.RECEIVED_CONFIGURATIONS_LIST:
      return {
        ...state,
        activePage,
        items: response.results,
        total: response.count,
        pages: Math.ceil(response.count / itemsPerPage)
      };

    default:
      return state;
  }
}
