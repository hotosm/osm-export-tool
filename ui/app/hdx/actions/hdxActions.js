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
