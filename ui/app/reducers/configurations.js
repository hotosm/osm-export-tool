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

    case types.CONFIGURATION_CREATED:
    case types.CONFIGURATION_UPDATED:
    case types.CONFIGURATION_DELETED:
      return initialState;

    default:
      return state;
  }
}
