import axios from 'axios';
import cookie from 'react-cookie';
import types from './actionTypes';
import { startSubmit, stopSubmit, change } from 'redux-form';

export function createConfiguration(data,form_name) {
  return dispatch => {
    dispatch(startSubmit(form_name));
    return axios({
      url:'/api/configurations',
      method:'POST',
      contentType: 'application/json; version=1.0',
      data,
      headers: {
        'X-CSRFToken': cookie.load('csrftoken')
      }
    }).then(rsp => {
      console.log("Success")
    }).catch(err => {
      console.log("ERROR")
      console.warn(err)
      return dispatch(stopSubmit(form_name, {
        ...err.response.data,
        _error: 'Your configuration is invalid. Please check the fields above.'
      }));
    })
  }
}

export function getConfigurations(dispatch) {
  return axios({
    url:'/api/configurations'
  }).then(rsp => {
    dispatch({
      type: types.RECEIVED_CONFIGURATIONS_LIST,
      configurations:rsp.data
    })
  })
  .catch(error => {
    console.log(error)
    console.log("ERROR")
  })
}

export function getConfiguration(uid) {
  return dispatch => {
    return axios({
      url:`/api/configurations/${uid}`
    }).then(rsp => {
      console.log(rsp.data)
      dispatch({
        type: types.RECEIVED_CONFIGURATION,
        configuration:rsp.data
      })
      dispatch({
        type:"@@redux-form/INITIALIZE",
        meta:{form:"ConfigurationForm"},
        payload:rsp.data
      })
    })
    .catch(error => {
      console.log(error)
      console.log("ERROR")
    })
  }
}
