import { LOGIN_FAILURE, LOGOUT } from "redux-implicit-oauth2";

import types from "../actions";

const initialState = {};

export default function meta(
  state = initialState,
  { permissions, type, username }
) {
  switch (type) {
    case LOGIN_FAILURE:
    case LOGOUT:
      return initialState;

    case types.RECEIVED_PERMISSIONS:
      return {
        ...state,
        user: {
          ...state.user,
          permissions,
          username
        }
      };

    default:
      return state;
  }
}
