import {Config} from '../config';
import types from './actionTypes';
import axios from 'axios'
import cookie from 'react-cookie'

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

export const submitJob = data => dispatch => {
    dispatch({
        type: types.SUBMITTING_JOB
    });

    const csrfmiddlewaretoken = cookie.load('csrftoken');
    return axios({
        url: '/api/jobs',
        method: 'POST',
        contentType: 'application/json; version=1.0',
        data: data,
        headers: {"X-CSRFToken": csrfmiddlewaretoken}
    }).then((response) => {
        dispatch({
            type: types.JOB_SUBMITTED_SUCCESS,
            jobuid: response.data.uid

        });
    }).catch((error) => {console.log(error)
        dispatch({
            type: types.JOB_SUBMITTED_ERROR, error: error
        });
    });
}

export const getProviders = () => dispatch => {
    dispatch({
        type: types.GETTING_PROVIDERS
    });

    axios.get('/api/providers').catch((error) => {
        console.log(error);
    });

    return axios({
        url: '/api/providers',
        method: 'GET',
    }).then((response) => {
        dispatch({
            type: types.PROVIDERS_RECEIVED,
            providers: response.data
        });
    }).catch((error) => {
        console.log(error);
    });
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



