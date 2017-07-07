import types from "../actions";

const initialState = {
  items: [],
  total: null,
  nextPageUrl: null,
  prevPageUrl: null
};

export default function jobs(state = initialState, action) {
  switch (action.type) {
    case types.RECEIVED_EXPORT_LIST:
      return {
        ...state,
        nextPageUrl: action.response.next,
        prevPageUrl: action.response.previous,
        items: action.response.results.map(job => ({
          ...job,
          simplified_geom: {
            ...job.simplified_geom,
            id: job.simplified_geom.id || Math.random()
          }
        })),
        total: action.response.count
      };

    default:
      return state;
  }
}
