import axios from "axios";
import isEqual from "lodash/isEqual";

import { selectAuthToken } from "../../selectors";

export const getGeonames = query => (dispatch, getState) => {
  const token = selectAuthToken(getState());

  dispatch({ type: "FETCHING_GEONAMES" });

  return axios({
    baseURL: window.EXPORTS_API_URL,
    headers: {
      Authorization: `Bearer ${token}`
    },
    params: {
      q: query
    },
    url: "/api/request_geonames"
  })
    .then(response => response.data)
    .then(responseData => {
      const data = responseData.geonames;
      const geonames = [];

      for (var i = 0; i < data.length; i++) {
        if (
          (data[i].bbox && !isEqual(data[i].bbox, {})) ||
          (data.lat && data.lng)
        ) {
          geonames.push(data[i]);
        }
      }

      dispatch({ type: "RECEIVED_GEONAMES", geonames: geonames });
    })
    .catch(error => dispatch({ type: "GEONAMES_ERROR", error: error }));
};

export const getNominatim = params => (dispatch, getState) => {
  const token = selectAuthToken(getState());

  dispatch({ type: "FETCHING_NOMINATIM" });

  return axios({
    baseURL: window.EXPORTS_API_URL,
    headers: {
      Authorization: `Bearer ${token}`
    },
    params: params,
    url: "/api/request_nominatim"
  })
    .then(response => response.data)
    .then(responseData => {
      dispatch({ type: "RECEIVED_NOMINATIM", nominatim: responseData });
      return responseData
    })
    .catch(error => dispatch({ type: "NOMINATIM_ERROR", error: error }));
};
