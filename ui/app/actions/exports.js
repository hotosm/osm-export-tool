import axios from "axios";
import types from ".";
import { push } from "react-router-redux";
import { initialize, startSubmit, stopSubmit } from "redux-form";
import moment from "moment";

import { selectAuthToken } from "../selectors";

export const createExport = (data, formName) => (dispatch, getState) => {
  const token = selectAuthToken(getState());

  dispatch(startSubmit(formName));

  return axios({
    baseURL: window.EXPORTS_API_URL,
    headers: {
      Authorization: `Bearer ${token}`
    },
    url: "/api/jobs",
    method: "POST",
    contentType: "application/json; version=1.0",
    data
  })
    .then(rsp => {
      dispatch(stopSubmit(formName));
      dispatch(push(`/exports/${rsp.data.uid}`));
    })
    .catch(err =>
      dispatch(
        stopSubmit(formName, {
          ...err.response.data,
          _error:
            "Your export is invalid. Please check each page of the form for errors."
        })
      )
    );
};

export const cloneExport = e => (dispatch, getState) => {
  const token = selectAuthToken(getState());

  dispatch(push("/exports/new"));

  return axios({
    baseURL: window.EXPORTS_API_URL,
    headers: {
      Authorization: `Bearer ${token}`
    },
    url: `/api/jobs/${e.uid}/geom`
  })
    .then(rsp =>
      dispatch(
        initialize("ExportForm", {
          buffer_aoi: e.buffer_aoi,
          description: e.description,
          event: e.event,
          export_formats: e.export_formats,
          feature_selection: e.feature_selection,
          name: e.name,
          published: e.published,
          the_geom: rsp.data.the_geom,
          aoi: {
            description: "Cloned Area",
            geomType: "Polygon",
            title: "Custom Polygon"
          }
        })
      )
    )
    .catch(err => console.warn(err));
};

export const getRuns = jobUid => (dispatch, getState) => {
  const token = selectAuthToken(getState());

  return axios({
    baseURL: window.EXPORTS_API_URL,
    headers: {
      Authorization: `Bearer ${token}`
    },
    url: `/api/runs?job_uid=${jobUid}`
  }).then(rsp =>
    dispatch({
      type: types.RECEIVED_RUNS,
      id: jobUid,
      runs: rsp.data
    })
  );
};

export const runExport = jobUid => (dispatch, getState) => {
  const token = selectAuthToken(getState());

  dispatch({
    type: types.RUNNING_EXPORT,
    id: jobUid
  });

  return axios({
    baseURL: window.EXPORTS_API_URL,
    headers: {
      Authorization: `Bearer ${token}`
    },
    url: `/api/runs?job_uid=${jobUid}`,
    method: "POST"
  }).then(rsp => dispatch(getRuns(jobUid)));
};

export const getOverpassTimestamp = () => (dispatch, getState) => {
  const token = selectAuthToken(getState());

  return axios({
    baseURL: window.EXPORTS_API_URL,
    headers: {
      Authorization: `Bearer ${token}`
    },
    url: "/api/overpass_timestamp"
  })
    .then(rsp =>
      dispatch({
        type: types.RECEIVED_OVERPASS_TIMESTAMP,
        lastUpdated: moment(rsp.data.timestamp).fromNow()
      })
    )
    .catch(err => console.warn(err));
};

export const getExport = id => (dispatch, getState) => {
  const token = selectAuthToken(getState());

  return axios({
    baseURL: window.EXPORTS_API_URL,
    headers: {
      Authorization: `Bearer ${token}`
    },
    url: `/api/jobs/${id}`
  }).then(rsp =>
    dispatch({
      type: types.RECEIVED_EXPORT,
      id: id,
      job: rsp.data
    })
  );
};

export const getExports = (filters = {}, page = 1) => (dispatch, getState) => {
  const itemsPerPage = 20;
  const token = selectAuthToken(getState());

  dispatch({
    type: types.FETCHING_EXPORT_LIST
  });

  return axios({
    baseURL: window.EXPORTS_API_URL,
    headers: {
      Authorization: `Bearer ${token}`
    },
    params: {
      ...filters,
      limit: itemsPerPage,
      offset: Math.max(0, (page - 1) * itemsPerPage)
    },
    url: "/api/jobs"
  })
    .then(({ data: response }) =>
      dispatch({
        type: types.RECEIVED_EXPORT_LIST,
        activePage: page,
        itemsPerPage,
        response
      })
    )
    .catch(error =>
      dispatch({
        type: types.FETCHING_EXPORT_LIST_FAILED,
        error,
        statusCode: error.response && error.response.status
      })
    );
};

// TODO this should be managed beneath the ExportAOI component
export function updateMode(mode) {
  return {
    type: types.SET_MODE,
    mode: mode
  };
}
