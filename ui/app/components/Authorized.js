import React from "react";
import { connect } from "react-redux";
import { withRouter } from "react-router-dom";
import { loginSuccess } from "../actions/meta";

class Authorized extends React.Component {
  componentDidMount() {
    // grab the hash fragment (e.g. "#access_token=…&expires_in=…")
    const hash = window.location.hash.replace(/^#/, "");
    const params = new URLSearchParams(hash);
    const token = params.get("access_token");
    const expiresIn = params.get("expires_in");

    if (token) {

      const expiresAt = expiresIn
        ? Date.now() + parseInt(expiresIn, 10) * 1000
        : null;


      this.props.loginSuccess(token, expiresAt);

      window.location.hash = "";
      this.props.history.replace("/");
    } else {
      // no token? bounce back to login/start
      this.props.history.replace("/");
    }
  }

  render() {
    return null;
  }
}

export default withRouter(
  connect(
    null,
    { loginSuccess }
  )(Authorized)
);