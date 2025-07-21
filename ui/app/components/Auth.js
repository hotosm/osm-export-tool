import React from "react";
import { connect } from "react-redux";
import { withRouter } from "react-router-dom";

import { fetchPermissions, loginSuccess } from "../actions/meta";
import { selectIsLoggedIn, selectLocationHash } from "../selectors";

class Auth extends React.Component {
  componentDidMount() {
    const {
      hash: { access_token, expires_in },
      isLoggedIn,
      loginSuccess,
      fetchPermissions,
      history,
      location
    } = this.props;

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
    { fetchPermissions, loginSuccess }
  )(Auth)
);