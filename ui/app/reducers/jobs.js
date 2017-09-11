import types from "../actions";

const initialState = {
  items: []
};

export default function jobs(state = initialState, { activePage, itemsPerPage, response, type }) {
  switch (type) {
    case types.RECEIVED_EXPORT_LIST:
      return {
        ...state,
        activePage,
        items: response.results.map(job => ({
          ...job,
          simplified_geom: {
            ...job.simplified_geom,
            id: job.simplified_geom.id || Math.random()
          }
        })),
        total: response.count,
        pages: Math.ceil(response.count / itemsPerPage)
      };

    case types.EXPORT_DELETED:
      return initialState;

    default:
      return state;
  }
}
