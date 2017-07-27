import { Component } from "react";
import { connect } from "react-redux";

import { fetchPermissions, loginSuccess } from "../actions/meta";
import { selectIsLoggedIn, selectLocationHash } from "../selectors";
import { history } from "../config/store";

class Auth extends Component {
  componentDidMount() {
    const {
      fetchPermissions,
      hash: { access_token, expires_in },
      isLoggedIn,
      loginSuccess
    } = this.props;

    if (isLoggedIn) {
      fetchPermissions();
    } else if (access_token != null) {
      loginSuccess(access_token, expires_in);
      history.replace("/");
    }
  }

  componentWillUpdate(nextProps, nextState) {
    const { fetchPermissions, isLoggedIn: wasLoggedIn } = this.props;
    const { isLoggedIn } = nextProps;

    if (!wasLoggedIn && isLoggedIn) {
      fetchPermissions();
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

export default connect(mapStateToProps, { fetchPermissions, loginSuccess })(
  Auth
);
