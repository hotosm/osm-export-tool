import axios from "axios";
import { push } from "react-router-redux";
import { startSubmit, stopSubmit } from "redux-form";

import types from ".";
import { selectAuthToken, selectLocationOptions } from "../selectors";

const launderExportRegion = exportRegion => {
  if (exportRegion.last_run != null) {
    exportRegion.last_run = new Date(exportRegion.last_run);
  }

  if (exportRegion.next_run != null) {
    exportRegion.next_run = new Date(exportRegion.next_run);
  }

  exportRegion.simplified_geom.id = exportRegion.id;

  return exportRegion;
};

export const getExportRegions = (filters = {}, page = 1) => (
  dispatch,
  getState
) => {
  const itemsPerPage = 5;
  const token = selectAuthToken(getState());

  dispatch({
    type: types.FETCHING_EXPORT_REGIONS
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
    url: "/api/partner_export_regions"
  })
    .then(rsp => {
      const exportRegions = rsp.data.results.map(launderExportRegion);

      dispatch({
        type: types.RECEIVED_EXPORT_REGIONS,
        activePage: page,
        itemsPerPage,
        response: {
          count: rsp.data.count,
          results: exportRegions
        }
      });
    })
    .catch(error =>
      dispatch({
        type: types.FETCH_EXPORT_REGIONS_ERROR,
        error,
        statusCode: error.response && error.response.status
      })
    );
};

export const getExportRegion = id => (dispatch, getState) => {
  const token = selectAuthToken(getState());

  dispatch({
    type: types.FETCHING_EXPORT_REGION,
    id
  });

  return axios({
    baseURL: window.EXPORTS_API_URL,
    headers: {
      Authorization: `Bearer ${token}`
    },
    url: `/api/partner_export_regions/${id}`
  })
    .then(rsp => rsp.data)
    .then(launderExportRegion)
    .then(exportRegion =>
      dispatch({
        type: types.RECEIVED_EXPORT_REGION,
        id,
        exportRegion
      })
    )
    .catch(error =>
      dispatch({
        type: types.FETCH_EXPORT_REGIONS_ERROR,
        id,
        error,
        statusCode: error.response && error.response.status
      })
    );
};

export const runExport = (id, jobUid) => (dispatch, getState) => {
  const token = selectAuthToken(getState());

  dispatch({
    type: types.STARTING_EXPORT_REGION_RUN,
    id
  });

  return axios({
    baseURL: window.EXPORTS_API_URL,
    headers: {
      Authorization: `Bearer ${token}`
    },
    url: `/api/runs?job_uid=${jobUid}`,
    method: "POST"
  })
    .then(rsp =>
      dispatch({
        type: types.EXPORT_REGION_RUN_STARTED,
        id
      })
    )
    .then(() => dispatch(getExportRegion(id)))
    .catch(error =>
      dispatch({
        type: types.EXPORT_REGION_RUN_ERROR,
        id,
        error,
        statusCode: error.response && error.response.status
      })
    );
};

export const deleteExportRegion = id => (dispatch, getState) => {
  const token = selectAuthToken(getState());

  dispatch({
    type: types.STARTING_EXPORT_REGION_DELETE,
    id
  });

  return axios({
    baseURL: window.EXPORTS_API_URL,
    headers: {
      Authorization: `Bearer ${token}`
    },
    url: `/api/partner_export_regions/${id}`,
    method: "DELETE"
  })
    .then(rsp => {
        dispatch({
          type: types.EXPORT_REGION_DELETED,
          id
        })
        dispatch(push(`/partners`))
      }
    )
    .catch(error =>
      dispatch({
        type: types.DELETE_EXPORT_REGION_ERROR,
        id,
        error,
        statusCode: error.response && error.response.status
      })
    );
};

export const zoomToExportRegion = id => dispatch =>
  dispatch({
    type: types.ZOOM_TO_EXPORT_REGION,
    id
  });

export const createExportRegion = (data, form) => (dispatch, getState) => {
  const token = selectAuthToken(getState());

  dispatch(startSubmit(form));

  return axios({
    baseURL: window.EXPORTS_API_URL,
    headers: {
      Authorization: `Bearer ${token}`
    },
    url: "/api/partner_export_regions",
    method: "POST",
    contentType: "application/json; version=1.0",
    data
  })
    .then(rsp => {
      console.log("Success");

      console.log("id:", rsp.data.id);

      dispatch(stopSubmit(form));

      dispatch({
        type: types.EXPORT_REGION_CREATED,
        id: data.id,
        exportRegion: rsp.data
      });

      dispatch(push(`/partners/edit/${rsp.data.id}`));
    })
    .catch(err => {
      console.warn(err);

      if (err.response) {
        var msg =
          "Your export region is invalid. Please check the fields above.";
        if ("the_geom" in err.response.data) {
          msg += " Choose an area to the right.";
        }
        return dispatch(
          stopSubmit(form, {
            ...err.response.data,
            _error: msg
          })
        );
      }

      return dispatch(
        stopSubmit(form, {
          _error: "Export region creation failed."
        })
      );
    });
};

// TODO this is practically identical to createExportRegion
export const updateExportRegion = (id, data, form) => (dispatch, getState) => {
  const token = selectAuthToken(getState());

  dispatch(startSubmit(form));

  return axios({
    baseURL: window.EXPORTS_API_URL,
    headers: {
      Authorization: `Bearer ${token}`
    },
    url: `/api/partner_export_regions/${id}`,
    method: "PUT",
    contentType: "application/json; version=1.0",
    data
  })
    .then(rsp => {
      console.log("Success");

      dispatch(stopSubmit(form));

      dispatch({
        type: types.EXPORT_REGION_UPDATED,
        id,
        exportRegion: rsp.data
      });
    })
    .catch(err => {
      console.warn(err);

      if (err.response) {
        return dispatch(
          stopSubmit(form, {
            ...err.response.data,
            _error:
              "Your export region is invalid. Please check the fields above."
          })
        );
      }

      return dispatch(
        stopSubmit(form, {
          _error: "Export region creation failed."
        })
      );
    });
};
