import axios from "axios";
import cookie from "react-cookie";
import types from ".";
import { push } from "react-router-redux";
import { initialize, startSubmit, stopSubmit } from "redux-form";
import moment from "moment";

export function createExport(data, formName) {
  return dispatch => {
    dispatch(startSubmit(formName));
    return axios({
      url: "/api/jobs",
      method: "POST",
      contentType: "application/json; version=1.0",
      data,
      headers: {
        "X-CSRFToken": cookie.load("csrftoken")
      }
    })
      .then(rsp => {
        dispatch(stopSubmit(formName));
        dispatch(push(`/exports/detail/${rsp.data.uid}`));
      })
      .catch(err => {
        var msg =
          "Your export is invalid. Please check each page of the form for errors.";
        return dispatch(
          stopSubmit(formName, {
            ...err.response.data,
            _error: msg
          })
        );
      });
  };
}

export function cloneExport(e) {
  return dispatch => {
    dispatch(push("/exports/new"));

    // TODO fetch the_geom rather than using simplified_geom

    dispatch(
      initialize("ExportForm", {
        buffer_aoi: e.buffer_aoi,
        description: e.description,
        event: e.event,
        export_formats: e.export_formats,
        feature_selection: e.feature_selection,
        name: e.name,
        published: e.published,
        the_geom: e.simplified_geom,
        aoi: {
          description: "Cloned Area",
          geomType: "Polygon",
          title: "Custom Polygon"
        }
      })
    );
  };
}

export function runExport(jobUid) {
  return dispatch => {
    return axios({
      url: `/api/runs?job_uid=${jobUid}`,
      method: "POST",
      headers: {
        "X-CSRFToken": cookie.load("csrftoken")
      }
    });
  };
}

export function getOverpassTimestamp() {
  return dispatch =>
    axios({
      url: "/api/overpass_timestamp"
    }).then(rsp => {
      dispatch({
        type: types.RECEIVED_OVERPASS_TIMESTAMP,
        lastUpdated: moment(rsp.data.timestamp).fromNow()
      });
    });
}

export function getExport(id) {
  return dispatch => {
    return axios({
      url: `/api/jobs/${id}`
    }).then(rsp => {
      dispatch({
        type: types.RECEIVED_EXPORT,
        id: id,
        job: rsp.data
      });
    });
  };
}

export function getExports(page = 1) {
  const itemsPerPage = 20;

  return dispatch => {
    return axios({
      params: {
        limit: itemsPerPage,
        offset: Math.max(0, (page - 1) * itemsPerPage)
      },
      url: "/api/jobs"
    }).then(({ data: response }) => {
      dispatch({
        type: types.RECEIVED_EXPORT_LIST,
        activePage: page,
        itemsPerPage,
        response
      });
    });
  };
}

export function getRuns(jobUid) {
  return dispatch => {
    return axios({
      url: `/api/runs?job_uid=${jobUid}`
    }).then(rsp => {
      dispatch({
        type: types.RECEIVED_RUNS,
        id: jobUid,
        runs: rsp.data
      });
    });
  };
}

// TODO this should be managed beneath the ExportAOI component
export function updateMode(mode) {
  return {
    type: types.SET_MODE,
    mode: mode
  };
}
