import axios from "axios";

import { selectAuthToken } from "../selectors";
import types from ".";

export const fetchPermissions = () => (dispatch, getState) => {
  const token = selectAuthToken(getState());

  dispatch({
    type: types.FETCHING_PERMISSIONS
  });

  // TODO export an instance configured with axios.create
  return axios({
    headers: {
      Authorization: `Bearer ${token}`
    },
    url: process.env.EXPORTS_API_URL + "/api/permissions"
  })
    .then(rsp =>
      dispatch({
        type: types.RECEIVED_PERMISSIONS,
        permissions: rsp.data.permissions
      })
    )
    .catch(error =>
      dispatch({
        type: types.FETCHING_PERMISSIONS_FAILED,
        error
      })
    );
};
