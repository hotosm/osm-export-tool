import types from "../actions";

const initialState = {
  fetching: false,
  fetched: false,
  exportRegions: {},
  items: []
};

export default function partners(
  state = initialState,
  {
    error,
    exportRegion,
    exportRegions,
    id,
    statusCode,
    total,
    type,
    locationOptions,
    activePage,
    itemsPerPage,
    response
  }
) {
  switch (type) {
    case types.FETCHING_EXPORT_REGION:
      return {
        ...state,
        fetching: true,
        fetched: false,
        error: null,
        status: null
      };

    case types.FETCHING_EXPORT_REGIONS:
      return {
        ...state,
        fetching: true,
        fetched: false,
        error: null,
        status: null
      };

    case types.RECEIVED_EXPORT_REGION:
      return {
        ...state,
        fetching: false,
        fetched: true,
        exportRegions: {
          ...state.exportRegions,
          [id]: exportRegion
        },
        error: null,
        status: null
      };

    case types.RECEIVED_EXPORT_REGIONS:
      return {
        ...state,
        fetching: false,
        fetched: true,
        items: response.results,
        error: null,
        status: null,
        total: response.count,
        activePage,
        pages: Math.ceil(response.count / itemsPerPage)
      };

    case types.FETCH_EXPORT_REGIONS_ERROR:
      return {
        ...state,
        fetching: false,
        fetched: false,
        exportRegions: {},
        status: null,
        id,
        error,
        statusCode
      };

    default:
      return state;
  }
}
