import {Config} from '../config';
import types from './actionTypes';



export function updateAoiInfo(geojson, geomType, title, description,) {
    return {
        type: types.UPDATE_AOI_INFO,
        geojson: geojson,
        geomType,
        title,
        description,
    }
}

export function clearAoiInfo() {
    return {
        type: types.CLEAR_AOI_INFO,
    }
}

export function updateMode(mode) {
    return {
        type: types.SET_MODE,
        mode: mode
    }
}

export function closeDrawer() {
    return {
        type: types.CLOSE_DRAWER
    }
}

export function openDrawer() {
    return {
        type: types.OPEN_DRAWER
    }
}



