import types from "../actions";

const initialState = {
  box: "DEFAULT",
  free: "DEFAULT",
  mapView: "DEFAULT",
  import: "DEFAULT",
  search: "DEFAULT"
};

export default function toolbarIcons(
  state = initialState,
  action
) {
  switch (action.type) {
    case types.SET_BOX_SELECTED:
      return {
        box: "SELECTED",
        free: "INACTIVE",
        mapView: "INACTIVE",
        import: "INACTIVE",
        search: "INACTIVE"
      };

    case types.SET_FREE_SELECTED:
      return {
        box: "INACTIVE",
        free: "SELECTED",
        mapView: "INACTIVE",
        import: "INACTIVE",
        search: "INACTIVE"
      };

    case types.SET_VIEW_SELECTED:
      return {
        box: "INACTIVE",
        free: "INACTIVE",
        mapView: "SELECTED",
        import: "INACTIVE",
        search: "INACTIVE"
      };

    case types.SET_IMPORT_SELECTED:
      return {
        box: "INACTIVE",
        free: "INACTIVE",
        mapView: "INACTIVE",
        import: "SELECTED",
        search: "INACTIVE"
      };

    case types.SET_SEARCH_SELECTED:
      return {
        box: "INACTIVE",
        free: "INACTIVE",
        mapView: "INACTIVE",
        import: "INACTIVE",
        search: "SELECTED"
      };

    case types.SET_BUTTONS_DEFAULT:
      return {
        box: "DEFAULT",
        free: "DEFAULT",
        mapView: "DEFAULT",
        import: "DEFAULT",
        search: "DEFAULT"
      };

    default:
      return state;
  }
}
