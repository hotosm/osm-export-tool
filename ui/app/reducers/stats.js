import types from "../actions";

const initialState = {
  geoms: [],
  periods: []
};

export default function stats(state = initialState,{type,data}) {
  switch (type) {
    case types.RECEIVED_STATS:
      return {
        ...state,
        geoms:data.geoms,
        periods:data.periods
      };

    default:
      return state;
  }
}
