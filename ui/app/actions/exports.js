import axios from "axios";
import types from ".";
import { push } from "react-router-redux";
import { initialize, startSubmit, stopSubmit } from "redux-form";
import moment from "moment";
import fileDownload from "js-file-download";

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
          isClone: true,
          description: e.description,
          event: e.event,
          export_formats: e.export_formats,
          feature_selection: e.feature_selection,
          mbtiles_maxzoom: e.mbtiles_maxzoom,
          mbtiles_minzoom: e.mbtiles_minzoom,
          mbtiles_source: e.mbtiles_source,
          name: e.name,
          published: e.published,
          unfiltered: e.unfiltered,
          preserve_geom: e.preserve_geom,
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

export const deleteExport = e => async (dispatch, getState) => {
  const token = selectAuthToken(getState());

  try {
    await axios({
      baseURL: window.EXPORTS_API_URL,
      headers: {
        Authorization: `Bearer ${token}`
      },
      method: "DELETE",
      url: `/api/jobs/${e.uid}`
    });

    dispatch({
      type: types.EXPORT_DELETED,
      id: e.uid
    });
    dispatch(push("/exports"));
  } catch (err) {
    console.warn(err);
  }
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
  }).then(rsp => dispatch(getRuns(jobUid)))
  .catch(function (error) {
    if (error.response) {
      if(error.response.data.status == "PREVIOUS_RUN_IN_QUEUE"){
        alert("Please wait to complete previous RUN");
      }
      else{
        alert("Please wait : There is limit of one RUN per Minute");
      }
    }
    else {
      alert("Please wait : There is limit of one RUN per Minute");
    }
  });
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

export const getGalaxyTimestamp = () => (dispatch, getState) => {
  return axios({
    baseURL: "https://raw-data-api0.hotosm.org/v1/",
    url: "status/"
  })
    .then(response =>
      dispatch({
        type: types.RECEIVED_GALAXY_TIMESTAMP,
        // lastUpdated: response.data.last_updated
        lastUpdated: moment(response.data.lastUpdated).fromNow()

      })
    )
    .catch(err => console.warn(err));
};

export const getExport = id => (dispatch, getState) => {
  const token = selectAuthToken(getState());

  dispatch({
    type: types.FETCHING_EXPORT
  });

  return axios({
    baseURL: window.EXPORTS_API_URL,
    headers: {
      Authorization: `Bearer ${token}`
    },
    url: `/api/jobs/${id}`
  })
    .then(rsp =>
      dispatch({
        type: types.RECEIVED_EXPORT,
        id: id,
        job: rsp.data
      })
    )
    .catch(error =>
      dispatch({
        type: types.FETCHING_EXPORT_FAILED,
        error,
        statusCode: error.response && error.response.status
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
      all: filters.all || (token == null),
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

export const getStats = (filters) => (dispatch, getState) => {
  const token = selectAuthToken(getState());

  return axios({
    baseURL: window.EXPORTS_API_URL,
    headers: {
      Authorization: `Bearer ${token}`
    },
    url: `/api/stats`,
    params: filters
  }).then(rsp =>
    dispatch({
      type: types.RECEIVED_STATS,
      data: rsp.data
    })
  );
};

export const getCsv = (filters) => (dispatch, getState) => {
  const token = selectAuthToken(getState());
  filters.csv = true;
  return axios({
    baseURL: window.EXPORTS_API_URL,
    headers: {
      Authorization: `Bearer ${token}`
    },
    url: `/api/stats`,
    params: filters
  }).then(rsp => {
    console.log(rsp.data)
    fileDownload(rsp.data,'exports.csv');
  });
};

export const getrunCsv = (filters) => (dispatch, getState) => {
  const token = selectAuthToken(getState());
  filters.csv = true;
  return axios({
    baseURL: window.EXPORTS_API_URL,
    headers: {
      Authorization: `Bearer ${token}`
    },
    url: `/api/run_stats`,
    params: filters
  }).then(rsp => {
    console.log(rsp.data)
    fileDownload(rsp.data,'exports_run.csv');
  });
};