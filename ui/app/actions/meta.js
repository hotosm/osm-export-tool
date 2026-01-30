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

  if (window.OAUTH_CLIENT_ID == null && window.AUTH_PROVIDER !== "hanko") {
    console.error("OAUTH_CLIENT_ID is undefined; logging in will not work.")
  }
}

// Auth provider detection
const isHankoAuth = window.AUTH_PROVIDER === "hanko";
const hankoUrl = window.HANKO_URL || "";

const oauthConfig = {
  // url: window.EXPORTS_API_URL + "/o/openstreetmap_oauth2",
  url: window.EXPORTS_API_URL + "/o/authorize?approval_prompt=auto&response_type=token",
  client: window.OAUTH_CLIENT_ID,
  redirect: `${window.location.protocol}//${hostname}/authorized`
};

// Export auth config for components
export const authConfig = {
  isHankoAuth,
  hankoUrl
};

export const fetchPermissions = () => (dispatch, getState) => {
  const token = selectAuthToken(getState());

  dispatch({
    type: types.FETCHING_PERMISSIONS
  });

  // Configure request based on auth provider
  const requestConfig = {
    baseURL: window.EXPORTS_API_URL,
    url: "/api/permissions",
    withCredentials: isHankoAuth // Send cookies for Hanko auth
  };

  // Only add Authorization header for legacy auth
  if (!isHankoAuth && token) {
    requestConfig.headers = {
      Authorization: `Bearer ${token}`
    };
  }

  return axios(requestConfig)
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

  // Configure request based on auth provider
  const requestConfig = {
    baseURL: window.EXPORTS_API_URL,
    url: "/api/groups",
    withCredentials: isHankoAuth // Send cookies for Hanko auth
  };

  // Only add Authorization header for legacy auth
  if (!isHankoAuth && token) {
    requestConfig.headers = {
      Authorization: `Bearer ${token}`
    };
  }

  return axios(requestConfig)
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

export const checkHankoAuth = () => (dispatch) => {
  if (!isHankoAuth) return;

  return axios({
    baseURL: window.EXPORTS_API_URL,
    url: "/api/auth/me/",
    withCredentials: true
  })
    .then(rsp => {
      if (rsp.data && rsp.data.auth_provider === "hanko") {
        // Set isLoggedIn = true by dispatching LOGIN_SUCCESS with a placeholder token
        dispatch({
          type: LOGIN_SUCCESS,
          token: "hanko-cookie-auth",
          expiresAt: null
        });
        dispatch(fetchPermissions());
      }
    })
    .catch(() => {
      // Not authenticated — nothing to do
    });
};

export const login = () => {
  if (isHankoAuth) {
    // Redirect to Hanko login with return URL
    const returnUrl = encodeURIComponent(window.location.href);
    window.location.href = `${hankoUrl}/app?return_to=${returnUrl}`;
  } else {
    // Legacy OAuth2 login
    const { url, client, redirect } = oauthConfig;
    window.location.href =
      url +
      `&client_id=${client}` +
      `&redirect_uri=${encodeURIComponent(redirect)}`;
  }
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

  if (isHankoAuth) {
    // For Hanko, clear cookies and redirect to logout
    // The hotosm-auth component handles the actual logout
    document.cookie.split(";").forEach(c => {
      document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/");
    });
  }

  dispatch(_logout());
};