import types from "../actions";

const initialState = {
  geojson: {},
  geomType: null,
  title: null,
  description: null
};

export default function aoiInfo(state = initialState, action) {
  switch (action.type) {
    case types.UPDATE_AOI_INFO:
      return {
        geojson: action.geojson,
        geomType: action.geomType,
        title: action.title,
        description: action.description
      };

    case types.CLEAR_AOI_INFO:
      return {
        geojson: null,
        geomType: null,
        title: null,
        description: null
      };

    default:
      return state;
  }
}
