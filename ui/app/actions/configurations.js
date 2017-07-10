import axios from "axios";
import cookie from "react-cookie";
import types from ".";
import { push } from "react-router-redux";
import { initialize, startSubmit, stopSubmit } from "redux-form";

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

export function getConfigurations(page = 1) {
  const itemsPerPage = 20;

  return dispatch => {
    return axios({
      params: {
        limit: itemsPerPage,
        offset: Math.max(0, (page - 1) * itemsPerPage)
      },
      url: "/api/configurations"
    }).then(({ data: response }) => {
      dispatch({
        type: types.RECEIVED_CONFIGURATIONS_LIST,
        activePage: page,
        itemsPerPage,
        response
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

      dispatch(initialize("ConfigurationForm", rsp.data));
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
