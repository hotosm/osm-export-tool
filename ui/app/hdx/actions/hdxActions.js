import axios from 'axios';

import types from '../actions/actionTypes';

const launderExportRegion = (exportRegion) => {
  exportRegion.last_run = exportRegion.last_run != null ? new Date(exportRegion.last_run) : null;
  exportRegion.next_run = exportRegion.next_run != null ? new Date(exportRegion.next_run) : null;

  exportRegion.the_geom.id = exportRegion.id;

  return exportRegion;
}

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
        error
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
    .then(rsp => {
      return rsp.data;
    }).then(launderExportRegion)
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
        error
      });
    });
  };
}

export function zoomToExportRegion (id) {
  return dispatch => {
    dispatch({
      type: types.ZOOM_TO_EXPORT_REGION,
      id
    });
  };
}
