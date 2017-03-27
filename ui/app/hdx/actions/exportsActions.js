import {Config} from '../config';
import types from './actionTypes';

export function createExportRequest(exportData) {
    return {
        type: types.CREATE_EXPORT_SUCCESS,
        exportInfo: exportData
    }
}

export function exportInfoDone() {
    return {
        type: types.EXPORT_INFO_DONE,
        setExportPackageFlag: true
    }
}
export function exportInfoNotDone() {
    return {
        type: types.EXPORT_INFO_NOTDONE,
        setExportPackageFlag: false
    }
}

export function updateAoiInfo(geojson, geomType, title, description,) {
    return {
        type: types.UPDATE_AOI_INFO,
        geojson: geojson,
        geomType,
        title,
        description,
    }
}
export function updateExportInfo(exportName, datapackDescription, projectName, makePublic, providers, area_str, layers) {
    return {
        type: types.UPDATE_EXPORT_INFO,
        exportName : exportName,
        datapackDescription,
        projectName,
        makePublic,
        providers,
        area_str,
        layers,
    }
}

export function clearExportInfo() {
    return {
        type: types.CLEAR_EXPORT_INFO,
    }
}

export function stepperNextDisabled() {
    return {
        type: types.MAKE_STEPPER_INACTIVE,
        stepperNextEnabled: false
    }
}

export function stepperNextEnabled() {
    return {
        type: types.MAKE_STEPPER_ACTIVE,
        stepperNextEnabled: true
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



