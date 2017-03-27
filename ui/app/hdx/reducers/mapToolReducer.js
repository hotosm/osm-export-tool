import types from '../actions/mapToolActionTypes';
import initialState from './initialState';

export function toolbarIconsReducer(state = initialState.toolbarIcons, action) {
    switch(action.type) {
        case types.SET_BOX_SELECTED:
            return {
                box: "SELECTED",
                free: "INACTIVE",
                mapView: "INACTIVE",
                import: "INACTIVE",
                search: "INACTIVE",
            }
        case types.SET_FREE_SELECTED:
            return {
                box: "INACTIVE",
                free: "SELECTED",
                mapView: "INACTIVE",
                import: "INACTIVE",
                search: "INACTIVE",
            }
        case types.SET_VIEW_SELECTED:
            return {
                box: "INACTIVE",
                free: "INACTIVE",
                mapView: "SELECTED",
                import: "INACTIVE",
                search: "INACTIVE",
            }
        case types.SET_IMPORT_SELECTED:
            return {
                box: "INACTIVE",
                free: "INACTIVE",
                mapView: "INACTIVE",
                import: "SELECTED",
                search: "INACTIVE",
            }
        case types.SET_SEARCH_SELECTED:
            return {
                box: "INACTIVE",
                free: "INACTIVE",
                mapView: "INACTIVE",
                import: "INACTIVE",
                search: "SELECTED",
            }
        case types.SET_BUTTONS_DEFAULT:
            return {
                box: "DEFAULT",
                free: "DEFAULT",
                mapView: "DEFAULT",
                import: "DEFAULT",
                search: "DEFAULT",
            }
        default:
            return state;
    }
}

export function showImportModalReducer(state = initialState.showImportModal, action) {
    switch(action.type) {
        case types.SET_IMPORT_MODAL_STATE:
            return action.showImportModal;
        default:
            return state;
    }
}

export function importGeomReducer(state = initialState.importGeom, action) {
    switch(action.type) {
        case types.FILE_PROCESSING:
            return {processing: true, processed: false, geom: {}, error: null};
        case types.FILE_PROCESSED:
            return {processing: false, processed: true, geom: action.geom, error: null};
        case types.FILE_ERROR:
            return {processing: false, processed: false, geom: {}, error: action.error};
        case types.FILE_RESET:
            return {processing: false, processed: false, geom: {}, error: null};
        default:
            return state;
    }
}
