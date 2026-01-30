import React from "react";
import { connect } from "react-redux";
import { withRouter } from "react-router-dom";

import { fetchPermissions, loginSuccess, logout, checkHankoAuth, authConfig } from "../actions/meta";
import { selectIsLoggedIn, selectLocationHash } from "../selectors";

class Auth extends React.Component {
  componentDidMount() {
    const {
      hash: { access_token, expires_in },
      isLoggedIn,
      loginSuccess,
      fetchPermissions,
      checkHankoAuth,
      history,
      location
    } = this.props;

    // Hanko cookie-based auth: check session via /api/auth/me/
    if (authConfig.isHankoAuth) {
      checkHankoAuth();

      // Listen for web component events
      this._onHankoLogin = () => {
        checkHankoAuth();
      };
      this._onLogout = () => {
        this.props.logout();
      };
      document.addEventListener("hanko-login", this._onHankoLogin);
      document.addEventListener("logout", this._onLogout);
      return;
    }

    // Legacy OAuth2 flow
    if (access_token) {
      const expiresAt = expires_in
        ? Date.now() + parseInt(expires_in, 10) * 1000
        : null;

      loginSuccess(access_token, expiresAt);
      localStorage.setItem("access_token", access_token);
      if (expiresAt) localStorage.setItem("expires_at", expiresAt);

      fetchPermissions();

      window.location.hash = "";
      history.replace(location.pathname);
      return;
    }

    if (!isLoggedIn) {
      const storedToken = localStorage.getItem("access_token");
      const storedExpiry = localStorage.getItem("expires_at");
      if (storedToken) {
        const storedExpiresAt = storedExpiry
          ? parseInt(storedExpiry, 10)
          : null;
        if (!storedExpiresAt || storedExpiresAt > Date.now()) {
          loginSuccess(storedToken, storedExpiresAt);
        } else {
          // expired
          localStorage.removeItem("access_token");
          localStorage.removeItem("expires_at");
        }
      }
    }
    if (isLoggedIn) {
      fetchPermissions();
    }
  }

  componentWillUnmount() {
    if (this._onHankoLogin) {
      document.removeEventListener("hanko-login", this._onHankoLogin);
    }
    if (this._onLogout) {
      document.removeEventListener("logout", this._onLogout);
    }
  }

  componentDidUpdate(prevProps) {
    if (!prevProps.isLoggedIn && this.props.isLoggedIn) {
      this.props.fetchPermissions();
    }
  }

  render() {
    return null;
  }
}

const mapStateToProps = state => ({
  hash: selectLocationHash(state),
  isLoggedIn: selectIsLoggedIn(state)
});

export default withRouter(
  connect(
    mapStateToProps,
    { fetchPermissions, loginSuccess, logout, checkHankoAuth }
  )(Auth)
);
