import axios from "axios";
import { LOGIN_SUCCESS, logout as _logout } from "redux-implicit-oauth2";

import { selectAuthToken } from "../selectors";
import types from ".";

let hostname = window.location.hostname;

if (window.location.port) {
  hostname += `:${window.location.port}`;
}

if (window.RAW_DATA_API_URL == null) {
  window.RAW_DATA_API_URL = process.env.RAW_DATA_API_URL;
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
  // url: window.EXPORTS_API_URL + "/o/openstreetmap_oauth2",
  url: window.EXPORTS_API_URL + "/o/authorize?approval_prompt=auto&response_type=token",
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
        permissions: rsp.data.permissions,
        username: rsp.data.username
      })
    )
    .catch(error =>
      dispatch({
        type: types.FETCHING_PERMISSIONS_FAILED,
        error
      })
    );
};

export const fetchGroups = () => (dispatch, getState) => {
  const token = selectAuthToken(getState());

  dispatch({
    type: types.FETCHING_GROUPS
  });

  return axios({
    baseURL: window.EXPORTS_API_URL,
    headers: {
      Authorization: `Bearer ${token}`
    },
    url: "/api/groups"
  })
    .then(rsp =>
      dispatch({
        type: types.RECEIVED_GROUPS,
        groups: rsp.data.groups
      })
    )
    .catch(error =>
      dispatch({
        type: types.FETCHING_GROUPS_FAILED,
        error
      })
    );
};

export const login = () => {
  const { url, client, redirect } = oauthConfig;
  window.location.href =
    url +
    `&client_id=${client}` +
    `&redirect_uri=${encodeURIComponent(redirect)}`;
};

export const loginSuccess = (token, expiresAt) => dispatch =>
  dispatch({
    type: LOGIN_SUCCESS,
    token,
    expiresAt
  });

export const logout = () => dispatch => {
  localStorage.removeItem("access_token");
  localStorage.removeItem("expires_at");
  dispatch(_logout());
};