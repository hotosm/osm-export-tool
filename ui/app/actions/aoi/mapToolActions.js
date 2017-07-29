import path from "path";

import { feature, featureCollection } from "@turf/helpers";

import types from "..";

export function setBoxButtonSelected() {
  return { type: types.SET_BOX_SELECTED };
}

export function setFreeButtonSelected() {
  return { type: types.SET_FREE_SELECTED };
}

export function setMapViewButtonSelected() {
  return { type: types.SET_VIEW_SELECTED };
}

export function setImportButtonSelected() {
  return { type: types.SET_IMPORT_SELECTED };
}

export function setSearchAOIButtonSelected() {
  return { type: types.SET_SEARCH_SELECTED };
}

export function setAllButtonsDefault() {
  return { type: types.SET_BUTTONS_DEFAULT };
}

export function setImportModalState(visibility) {
  return {
    type: types.SET_IMPORT_MODAL_STATE,
    showImportModal: visibility
  };
}

export function resetGeoJSONFile() {
  return {
    type: types.FILE_RESET
  };
}

export function processGeoJSONFile(file) {
  return dispatch => {
    dispatch({ type: types.FILE_PROCESSING });

    const filename = file.name;
    const ext = path.extname(filename);

    if (![".json", ".geojson"].includes(ext)) {
      return dispatch({
        type: types.FILE_ERROR,
        error: "File must be .geojson NOT ." + ext
      });
    }

    const reader = new FileReader();

    reader.onload = () => {
      let geojson;

      try {
        geojson = JSON.parse(reader.result);
      } catch (e) {
        return dispatch({
          type: types.FILE_ERROR,
          error: "Could not parse GeoJSON"
        });
      }

      if (["Polygon", "MultiPolygon"].includes(geojson.type)) {
        return dispatch({
          type: types.FILE_PROCESSED,
          geojson: featureCollection([feature(geojson)])
        });
      }

      dispatch({
        type: types.FILE_ERROR,
        error: "Geometry must be Polygon type, not " + geojson.type
      });
    };

    reader.onerror = () => {
      dispatch({
        type: types.FILE_ERROR,
        error: "An error was encountered while reading your file"
      });
    };

    reader.readAsText(file);
  };
}
