import axios from "axios";
import { LOGIN_SUCCESS, login as _login, logout } from "redux-implicit-oauth2";

import { selectAuthToken } from "../selectors";
import types from ".";

let hostname = window.location.hostname;

if (window.location.port) {
  hostname += `:${window.location.port}`;
}

if (window.EXPORTS_API_URL == null) {
  window.EXPORTS_API_URL = process.env.EXPORTS_API_URL;

  if (window.EXPORTS_API_URL == null) {
    console.error("EXPORTS_API_URL is undefined; logging in will not work.")
  }
}

if (window.OAUTH_CLIENT_ID == null) {
  window.OAUTH_CLIENT_ID = process.env.CLIENT_ID;

  if (window.OAUTH_CLIENT_ID == null) {
    console.error("OAUTH_CLIENT_ID is undefined; logging in will not work.")
  }
}

const oauthConfig = {
  url: window.EXPORTS_API_URL + "/o/authorize?approval_prompt=auto",
  client: window.OAUTH_CLIENT_ID,
  redirect: `${window.location.protocol}//${hostname}/authorized`
};

export const fetchPermissions = () => (dispatch, getState) => {
  const token = selectAuthToken(getState());

  dispatch({
    type: types.FETCHING_PERMISSIONS
  });

  // TODO export an instance configured with axios.create
  return axios({
    baseURL: window.EXPORTS_API_URL,
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

export const loginSuccess = (token, expiresAt) => dispatch =>
  dispatch({
    type: LOGIN_SUCCESS,
    token,
    expiresAt
  });

export { logout };
