import axios from "axios";
import { push } from "react-router-redux";
import { initialize, startSubmit, stopSubmit } from "redux-form";

import { selectAuthToken } from "../selectors";
import types from ".";

export const createConfiguration = (data, formName) => (dispatch, getState) => {
  const token = selectAuthToken(getState());

  dispatch(startSubmit(formName));

  return axios({
    baseURL: process.env.EXPORTS_API_URL,
    headers: {
      Authorization: `Bearer ${token}`
    },
    url: "/api/configurations",
    method: "POST",
    contentType: "application/json; version=1.0",
    data
  })
    .then(rsp => console.log("Success"))
    .catch(err =>
      dispatch(
        stopSubmit(formName, {
          ...err.response.data,
          _error:
            "Your configuration is invalid. Please check the fields above."
        })
      )
    );
};

export const updateConfiguration = (uid, data, formName) => (
  dispatch,
  getState
) => {
  const token = selectAuthToken(getState());

  dispatch(startSubmit(formName));

  return axios({
    baseURL: process.env.EXPORTS_API_URL,
    headers: {
      Authorization: `Bearer ${token}`
    },
    url: `/api/configurations/${uid}`,
    method: "PUT",
    contentType: "application/json; version=1.0",
    data
  })
    .then(rsp => {
      console.log("Success");
    })
    .catch(err => {
      return dispatch(
        stopSubmit(formName, {
          ...err.response.data,
          _error:
            "Your configuration is invalid. Please check the fields above."
        })
      );
    });
};

export const getConfigurations = (filters = {}, page = 1) => (
  dispatch,
  getState
) => {
  const itemsPerPage = 20;
  const token = selectAuthToken(getState());

  return axios({
    baseURL: process.env.EXPORTS_API_URL,
    headers: {
      Authorization: `Bearer ${token}`
    },
    params: {
      ...filters,
      limit: itemsPerPage,
      offset: Math.max(0, (page - 1) * itemsPerPage)
    },
    url: "/api/configurations"
  }).then(({ data: response }) =>
    dispatch({
      type: types.RECEIVED_CONFIGURATIONS_LIST,
      activePage: page,
      itemsPerPage,
      response
    })
  );
};

export const getConfiguration = uid => (dispatch, getState) => {
  const token = selectAuthToken(getState());

  return axios({
    baseURL: process.env.EXPORTS_API_URL,
    headers: {
      Authorization: `Bearer ${token}`
    },
    url: `/api/configurations/${uid}`
  }).then(rsp => {
    dispatch({
      type: types.RECEIVED_CONFIGURATION,
      configuration: rsp.data
    });

    dispatch(initialize("ConfigurationForm", rsp.data));
  });
};

export const deleteConfiguration = uid => (dispatch, getState) => {
  const token = selectAuthToken(getState());

  return axios({
    baseURL: process.env.EXPORTS_API_URL,
    headers: {
      Authorization: `Bearer ${token}`
    },
    url: `/api/configurations/${uid}`,
    method: "DELETE"
  }).then(rsp => dispatch(push("/configurations")));
};
