import types from "../actions";

export default function showImportModal(state = false, action) {
  switch (action.type) {
    case types.SET_IMPORT_MODAL_STATE:
      return action.showImportModal;

    default:
      return state;
  }
}
