import { Component } from "react";
import { connect } from "react-redux";

import { selectPermissions } from "../selectors";

class RequirePermission extends Component {
  hasPermission() {
    const { permissions } = this.props;
    let { required } = this.props;

    if (required != null && !Array.isArray(required)) {
      required = Array.of(required);
    }

    return (
      (required == null && permissions != null) ||
      (permissions != null && required.every(p => permissions.includes(p)))
    );
  }

  render() {
    const { children } = this.props;

    if (this.hasPermission()) {
      return children;
    }

    return null;
  }
}

const mapStateToProps = state => ({
  permissions: selectPermissions(state)
});

export default connect(mapStateToProps)(RequirePermission);
