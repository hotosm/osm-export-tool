import axios from 'axios';
import cookie from 'react-cookie';
import {Config} from '../config';
import types from './actionTypes';
import { push } from 'react-router-redux';
import { startSubmit, stopSubmit } from 'redux-form';

export function createExport (data,form_name) {
  return dispatch => {
    dispatch(startSubmit(form_name));
    return axios({
      url: '/api/jobs',
      method: 'POST',
      contentType: 'application/json; version=1.0',
      data,
      headers: {
        'X-CSRFToken': cookie.load('csrftoken')
      }
    }).then(rsp => {
      console.log("SUCCESS")
      console.log("export uid: ", rsp.data.uid)
      dispatch(stopSubmit(form_name))
      dispatch(push(`/exports/detail/${rsp.data.uid}`));
    }).catch(err => {
      console.log("ERROR")
      console.warn(err)
      return dispatch(stopSubmit(form_name, {
        ...err.response.data,
        _error: 'Your export is invalid. Please check the fields above.'
      }));
    })

  }
}

export function getExport(id) {
  return dispatch => {
    return axios({
      url:`/api/jobs/${id}`
    }).then(rsp => {
      dispatch({
        type: types.RECEIVED_EXPORT,
        id:id,
        job:rsp.data
      })
    })
    .catch(error => {
      console.log("ERROR")
    })
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



