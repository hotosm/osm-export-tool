/* global OAUTH_CLIENT_ID: false */
import axios from "axios";
import { login as _login, logout } from "redux-implicit-oauth2";

import { selectAuthToken } from "../selectors";
import types from ".";

const oauthConfig = {
  url: process.env.EXPORTS_API_URL + "/o/authorize?approval_prompt=auto",
  client: OAUTH_CLIENT_ID || process.env.CLIENT_ID,
  redirect: `${window.location.protocol}//${window.location.hostname}/authorized`
};

export const fetchPermissions = () => (dispatch, getState) => {
  const token = selectAuthToken(getState());

  dispatch({
    type: types.FETCHING_PERMISSIONS
  });

  // TODO export an instance configured with axios.create
  return axios({
    baseURL: process.env.EXPORTS_API_URL,
    headers: {
      Authorization: `Bearer ${token}`
    },
    url: "/api/permissions"
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

export const login = () => _login(oauthConfig);

export { logout };
