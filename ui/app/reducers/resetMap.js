import types from "../actions";

const initialState = {
  click: false
};

export default function resetMap(state = initialState, action) {
  switch (action.type) {
    case types.CLICK_RESET_MAP:
      return {
        ...state,
        click: !state.click
      };

    default:
      return state;
  }
}
