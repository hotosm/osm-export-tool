import types from './mapToolActionTypes'
import ol from 'openlayers';

export function setBoxButtonSelected() {
    return {type: types.SET_BOX_SELECTED}
}

export function setFreeButtonSelected() {
    return {type: types.SET_FREE_SELECTED} 
}

export function setMapViewButtonSelected() {
    return {type: types.SET_VIEW_SELECTED}
}

export function setImportButtonSelected() {
    return {type: types.SET_IMPORT_SELECTED}
}

export function setSearchAOIButtonSelected() {
    return {type: types.SET_SEARCH_SELECTED}
}

export function setAllButtonsDefault() {
    return {type: types.SET_BUTTONS_DEFAULT}
}

export function setImportModalState(visibility) {
    return {
        type: types.SET_IMPORT_MODAL_STATE,
        showImportModal: visibility,
    }
}

export function resetGeoJSONFile() {
    return {
        type: types.FILE_RESET
    }
}

export function processGeoJSONFile(file) {
    return (dispatch) => {
        dispatch({type: types.FILE_PROCESSING});
        const fileName = file.name;
        const ext = fileName.split('.').pop();
        if(ext != 'geojson') {
            dispatch({type: types.FILE_ERROR, error: 'File must be .geojson NOT .' + ext});
            return;
        }
        const reader = new FileReader();
        reader.onload = () => {
            const dataURL = reader.result;
            let geojson = null;
            try {
                geojson = JSON.parse(dataURL);
            }
            catch (e) {
                dispatch({type: types.FILE_ERROR, error: 'Could not parse GeoJSON'});
                return;
            }
            const geojsonReader = new ol.format.GeoJSON();
            const feature = geojsonReader.readFeatures(geojson)[0];
            const geom = feature.getGeometry().transform('EPSG:4326', 'EPSG:3857');
            if(geom.getType() == 'Polygon') {
                dispatch({type: types.FILE_PROCESSED, geom: geom});
            }
            else {
                dispatch({type: types.FILE_ERROR, error: 'Geometry must be Polygon type, not ' + geom.getType()})
            }
        }
        reader.onerror = () => {
            dispatch({type: types.FILE_ERROR, error: 'An error was encountered while reading your file'});
        }
        reader.readAsText(file);
    }
}
