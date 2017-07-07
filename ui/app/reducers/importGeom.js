import types from "../actions";

const initialState = {
  processing: false,
  processed: false,
  geojson: {},
  error: null
};

export default function importGeom(state = initialState, action) {
  switch (action.type) {
    case types.FILE_PROCESSING:
      return { processing: true, processed: false, geojson: {}, error: null };

    case types.FILE_PROCESSED:
      return {
        processing: false,
        processed: true,
        geojson: action.geojson,
        error: null
      };

    case types.FILE_ERROR:
      return {
        processing: false,
        processed: false,
        geojson: {},
        error: action.error
      };

    case types.FILE_RESET:
      return { processing: false, processed: false, geojson: {}, error: null };

    default:
      return state;
  }
}
