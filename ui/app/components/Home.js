import React from "react";
import { connect } from "react-redux";
import { login, logout } from "redux-implicit-oauth2";

const config = {
  url: "http://localhost/o/authorize",
  client: "BAzRvOEMV6yyQflLu0GpN4Qn8sdFdwYbMn0EceAS",
  // TODO needs to be on the same host that the React app is served from
  // TODO can't be attached to react-router (w/ hash history), as the state will get cleared
  redirect: "http://localhost/foo"
};

const Login = ({ auth, isLoggedIn, login, logout }) => {
  console.log("auth:", auth)
  if (isLoggedIn) {
    return (
      <button type="button" onClick={logout}>
        Logout
      </button>
    );
  }

  return (
    <button type="button" onClick={login}>
      Login
    </button>
  );
};

const mapStateToProps = state => ({
  auth: state.auth,
  isLoggedIn: state.auth.isLoggedIn
});

export default connect(mapStateToProps, { login: () => login(config), logout })(
  Login
);
