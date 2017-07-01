import axios from 'axios';
import cookie from 'react-cookie';
import types from './actionTypes';
import { push } from 'react-router-redux';
import { startSubmit, stopSubmit } from 'redux-form';
import moment from 'moment'

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
      var msg = 'Your export is invalid. Please check each page of the form for errors.'
      if ('the_geom' in err.response.data) msg = msg + " Select an area to the right."
      return dispatch(stopSubmit(form_name, {
        ...err.response.data,
        _error: msg
      }));
    })

  }
}

export function cloneExport(e) {
  return dispatch => {
    dispatch(push('/exports/new'))

    dispatch(updateAoiInfo(e.the_geom,"Polygon","Custom Polygon","Cloned Area"))
    dispatch({
      type:"@@redux-form/INITIALIZE",
      meta:{form:"ExportForm"},
      payload:{
        buffer_aoi:e.buffer_aoi,
        description:e.description,
        event:e.event,
        export_formats:e.export_formats,
        feature_selection:e.feature_selection,
        name:e.name,
        published:e.published
      }
    })
  }
}

export function runExport (jobUid) {
  return dispatch => {
    return axios({
      url: `/api/runs?job_uid=${jobUid}`,
      method: 'POST',
      headers: {
        'X-CSRFToken': cookie.load('csrftoken')
      }
    })
  };
}


export function getOverpassTimestamp(dispatch) {
    return axios({
      url:'/api/overpass_timestamp'
    }).then(rsp => {
      dispatch({
        type: types.RECEIVED_OVERPASS_TIMESTAMP,
        lastUpdated:moment(rsp.data.timestamp).fromNow()
      })
    })
    .catch(error => {
      console.log("ERROR")
    })
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

export function getExports(dispatch) {
  return axios({
    url:'/api/jobs'
  }).then(rsp => {
    dispatch({
      type: types.RECEIVED_EXPORT_LIST,
      id:id,
      jobs:rsp.data
    })
  })
  .catch(error => {
    console.log("ERROR")
  })
}

export function getRuns(jobUid) {
  return dispatch => {
    return axios({
      url:`/api/runs?job_uid=${jobUid}`
    }).then(rsp => {
      dispatch({
        type: types.RECEIVED_RUNS,
        id:jobUid,
        runs:rsp.data
      })
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
