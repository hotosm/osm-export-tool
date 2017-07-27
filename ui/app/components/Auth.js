import { Component } from "react";
import { connect } from "react-redux";

import { fetchPermissions } from "../actions/meta";
import { selectIsLoggedIn } from "../selectors";

class Auth extends Component {
  componentDidMount() {
    const { fetchPermissions, isLoggedIn } = this.props;

    if (isLoggedIn) {
      fetchPermissions();
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
  isLoggedIn: selectIsLoggedIn(state)
});

export default connect(mapStateToProps, { fetchPermissions })(Auth);
