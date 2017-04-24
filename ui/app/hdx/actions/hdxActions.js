import axios from 'axios';
import cookie from 'react-cookie';
import { push } from 'react-router-redux';
import { startSubmit, stopSubmit } from 'redux-form';

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
      // convert to a keyed object
      return exportRegions.reduce((obj, x) => {
        obj[x.id] = x;

        return obj;
      }, {});
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

export function runExport (id, jobUid) {
  return dispatch => {
    dispatch({
      type: types.STARTING_EXPORT_REGION_RUN,
      id
    });

    return axios({
      url: `/api/runs?job_uid=${jobUid}`,
      method: 'POST',
      headers: {
        'X-CSRFToken': cookie.load('csrftoken')
      }
    })
    .then(rsp => dispatch({
      type: types.EXPORT_REGION_RUN_STARTED,
      id
    }))
    .then(() => dispatch(getExportRegion(id)))
    .catch(error => dispatch({
      type: types.EXPORT_REGION_RUN_ERROR,
      id,
      error,
      statusCode: error.response && error.response.status
    }));
  };
}

export function deleteExportRegion (id) {
  return dispatch => {
    dispatch({
      type: types.STARTING_EXPORT_REGION_DELETE,
      id
    });

    return axios({
      url: `/api/hdx_export_regions/${id}`,
      method: 'DELETE',
      headers: {
        'X-CSRFToken': cookie.load('csrftoken')
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

export function createExportRegion (form) {
  return data => {
    return dispatch => {
      dispatch(startSubmit(form));

      return axios({
        url: '/api/hdx_export_regions',
        method: 'POST',
        contentType: 'application/json; version=1.0',
        data,
        headers: {
          'X-CSRFToken': cookie.load('csrftoken')
        }
      }).then(rsp => {
        console.log('Success');

        console.log('id:', rsp.data.id);

        dispatch(stopSubmit(form));

        dispatch({
          type: types.EXPORT_REGION_CREATED,
          id: data.id,
          exportRegion: rsp.data
        });

        dispatch(push(`/edit/${rsp.data.id}`));
      }).catch(err => {
        console.warn(err);

        if (err.response) {
          return dispatch(stopSubmit(form, {
            ...err.response.data,
            _error: 'Your export region is invalid. Please check the fields above.'
          }));
        }

        return dispatch(stopSubmit(form, {
          _error: 'Export region creation failed.'
        }));
      });
    };
  };
}

export function updateExportRegion (form) {
  return (id, data) => {
    // TODO this is practically identical to createExportRegion
    return dispatch => {
      dispatch(startSubmit(form));

      return axios({
        url: `/api/hdx_export_regions/${id}`,
        method: 'PUT',
        contentType: 'application/json; version=1.0',
        data,
        headers: {
          'X-CSRFToken': cookie.load('csrftoken')
        }
      }).then(rsp => {
        console.log('Success');

        dispatch(stopSubmit(form));

        dispatch({
          type: types.EXPORT_REGION_UPDATED,
          id,
          exportRegion: rsp.data
        });
      }).catch(err => {
        console.warn(err);

        if (err.response) {
          return dispatch(stopSubmit(form, {
            ...err.response.data,
            _error: 'Your export region is invalid. Please check the fields above.'
          }));
        }

        return dispatch(stopSubmit(form, {
          _error: 'Export region creation failed.'
        }));
      });
    };
  };
}
