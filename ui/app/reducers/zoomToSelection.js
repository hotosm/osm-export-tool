import types from "../actions";

const initialState = {
  click: false
};

export default function zoomToSelection(state = initialState, action) {
  switch (action.type) {
    case types.CLICK_ZOOM_TO_SELECTION:
      return {
        ...state,
        click: !state.click
      };

    default:
      return state;
  }
}
