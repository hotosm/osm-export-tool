import axios from 'axios';

import types from '../actions/actionTypes';

export function getExportRegions () {
  return dispatch => {
    dispatch({
      type: types.FETCHING_EXPORT_REGIONS
    });

    return axios.get('/api/hdx_export_regions')
    .then(rsp => {
      return rsp.data;
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
    }).then(exportRegion => {
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
