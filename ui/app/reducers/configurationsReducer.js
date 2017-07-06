import types from "../actions/actionTypes";
import initialState from "./initialState";

export function configurationsReducer(
  state = initialState.configurations,
  action
) {
  switch (action.type) {
    case types.RECEIVED_CONFIGURATIONS_LIST:
      return {
        ...state,
        nextPageUrl: action.response.next,
        prevPageUrl: action.response.previous,
        items: action.response.results,
        total: action.response.count
      };
  }
  return state;
}
