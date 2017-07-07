import axios from "axios";
import cookie from "react-cookie";
import types from ".";
import { push } from "react-router-redux";
import { startSubmit, stopSubmit, change } from "redux-form";

export function createConfiguration(data, form_name) {
  return dispatch => {
    dispatch(startSubmit(form_name));
    return axios({
      url: "/api/configurations",
      method: "POST",
      contentType: "application/json; version=1.0",
      data,
      headers: {
        "X-CSRFToken": cookie.load("csrftoken")
      }
    })
      .then(rsp => {
        console.log("Success");
      })
      .catch(err => {
        return dispatch(
          stopSubmit(form_name, {
            ...err.response.data,
            _error:
              "Your configuration is invalid. Please check the fields above."
          })
        );
      });
  };
}

export function updateConfiguration(uid, data, form_name) {
  return dispatch => {
    dispatch(startSubmit(form_name));
    return axios({
      url: `/api/configurations/${uid}`,
      method: "PUT",
      contentType: "application/json; version=1.0",
      data,
      headers: {
        "X-CSRFToken": cookie.load("csrftoken")
      }
    })
      .then(rsp => {
        console.log("Success");
      })
      .catch(err => {
        return dispatch(
          stopSubmit(form_name, {
            ...err.response.data,
            _error:
              "Your configuration is invalid. Please check the fields above."
          })
        );
      });
  };
}

export function getConfigurations(url) {
  return dispatch => {
    return axios({
      url: url || "/api/configurations"
    }).then(rsp => {
      dispatch({
        type: types.RECEIVED_CONFIGURATIONS_LIST,
        response: rsp.data
      });
    });
  };
}

export function getConfiguration(uid) {
  return dispatch => {
    return axios({
      url: `/api/configurations/${uid}`
    }).then(rsp => {
      dispatch({
        type: types.RECEIVED_CONFIGURATION,
        configuration: rsp.data
      });
      dispatch({
        type: "@@redux-form/INITIALIZE",
        meta: { form: "ConfigurationForm" },
        payload: rsp.data
      });
    });
  };
}

export function deleteConfiguration(uid) {
  return dispatch => {
    return axios({
      url: `/api/configurations/${uid}`,
      method: "DELETE",
      headers: {
        "X-CSRFToken": cookie.load("csrftoken")
      }
    }).then(rsp => {
      dispatch(push("/configurations"));
    });
  };
}
