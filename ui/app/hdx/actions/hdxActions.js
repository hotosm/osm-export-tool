import axios from 'axios';

import types from '../actions/actionTypes';

const launderExportRegion = (exportRegion) => {
  if (exportRegion.last_run != null) {
    exportRegion.last_run = new Date(exportRegion.last_run);
  }

  if (exportRegion.next_run != null) {
    exportRegion.next_run = new Date(exportRegion.next_run);
  }

  exportRegion.the_geom.id = exportRegion.id;

  return exportRegion;
};

export function getExportRegions () {
  return dispatch => {
    dispatch({
      type: types.FETCHING_EXPORT_REGIONS
    });

    return axios.get('/api/hdx_export_regions')
    .then(rsp => {
      return rsp.data;
    }).then(exportRegions => {
      return exportRegions.map(launderExportRegion);
    }).then(exportRegions => {
      dispatch({
        type: types.RECEIVED_EXPORT_REGIONS,
        exportRegions
      });
    }).catch(error => {
      dispatch({
        type: types.FETCH_EXPORT_REGIONS_ERROR,
        error,
        statusCode: error.response && error.response.status
      });
    });
  };
}

export function getExportRegion (id) {
  return dispatch => {
    dispatch({
      type: types.FETCHING_EXPORT_REGION,
      id
    });

    return axios.get(`/api/hdx_export_regions/${id}`)
    .then(rsp => rsp.data)
    .then(launderExportRegion)
    .then(exportRegion => {
      dispatch({
        type: types.RECEIVED_EXPORT_REGION,
        id,
        exportRegion
      });
    }).catch(error => {
      dispatch({
        type: types.FETCH_EXPORT_REGIONS_ERROR,
        id,
        error,
        statusCode: error.response && error.response.status
      });
    });
  };
}

export function runExport (id) {
  return dispatch => {
    dispatch({
      type: types.STARTING_EXPORT_REGION_RUN,
      id
    });

    return axios.post(`/api/hdx_export_regions/${id}/run`)
    .then(rsp => dispatch({
      type: types.EXPORT_REGION_RUN_STARTED,
      id
    }))
    .catch(error => dispatch({
      type: types.EXPORT_REGION_RUN_ERROR,
      id,
      error,
      statusCode: error.response && error.response.status
    }));
  };
}

export function deleteExportRegion (id, csrfToken) {
  return dispatch => {
    dispatch({
      type: types.STARTING_EXPORT_REGION_DELETE,
      id
    });
    return axios({
      url: `/api/hdx_export_regions/${id}`,
      method: 'DELETE',
      headers: {
        'X-CSRFToken': csrfToken
      }
    })
    .then(rsp => dispatch({
      type: types.EXPORT_REGION_DELETED,
      id
    }))
    .catch(error => dispatch({
      type: types.DELETE_EXPORT_REGION_ERROR,
      id,
      error,
      statusCode: error.response && error.response.status
    }));
  };
}

export function zoomToExportRegion (id) {
  return dispatch => dispatch({
    type: types.ZOOM_TO_EXPORT_REGION,
    id
  });
}
