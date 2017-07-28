import React, { Component } from "react";
import { FormattedMessage } from "react-intl";
import { connect } from "react-redux";

import styles from "../../styles/aoi/DrawAOIToolbar.css";
import {
  setMapViewButtonSelected,
  setAllButtonsDefault
} from "../../actions/aoi/mapToolActions";

const DEFAULT_ICON = (
  <div>
    <i className={"material-icons " + styles.defaultButton}>
      settings_overscan
    </i>
    <div className={styles.buttonName}>
      <FormattedMessage
        id="ui.draw.current_view"
        defaultMessage="CURRENT VIEW"
      />
    </div>
  </div>
);

const INACTIVE_ICON = (
  <div>
    <i className={"material-icons " + styles.inactiveButton}>
      settings_overscan
    </i>
    <div className={styles.buttonName + " " + styles.buttonNameInactive}>
      <FormattedMessage
        id="ui.draw.current_view"
        defaultMessage="CURRENT VIEW"
      />
    </div>
  </div>
);

const SELECTED_ICON = (
  <div>
    <i className={"material-icons " + styles.selectedButton}>clear</i>
    <div className={styles.buttonName}>
      <FormattedMessage
        id="ui.draw.current_view"
        defaultMessage="CURRENT VIEW"
      />
    </div>
  </div>
);

export class MapViewButton extends Component {
  state = {
    icon: DEFAULT_ICON
  };

  componentWillReceiveProps(nextProps) {
    // TODO state is wholely unnecessary
    //If the button has been selected update the button state
    if (nextProps.toolbarIcons.mapView === "SELECTED") {
      this.setState({ icon: SELECTED_ICON });
    }
    // If the button has been de-selected update the button state
    if (nextProps.toolbarIcons.mapView === "DEFAULT") {
      this.setState({ icon: DEFAULT_ICON });
    }
    // If the button has been set as inactive update the state
    if (nextProps.toolbarIcons.mapView === "INACTIVE") {
      this.setState({ icon: INACTIVE_ICON });
    }
  }

  handleOnClick = () => {
    if (this.state.icon === SELECTED_ICON) {
      this.props.setAllButtonsDefault();
      this.props.handleCancel();
    } else if (this.state.icon === DEFAULT_ICON) {
      this.props.setMapViewButtonSelected();
      this.props.setMapView();
    }
  };

  render() {
    return (
      <div className={styles.drawButtonGeneral} onClick={this.handleOnClick}>
        {this.state.icon}
      </div>
    );
  }
}

function mapStateToProps(state) {
  return {
    toolbarIcons: state.toolbarIcons
  };
}

export default connect(mapStateToProps, {
  setAllButtonsDefault,
  setMapViewButtonSelected
})(MapViewButton);
