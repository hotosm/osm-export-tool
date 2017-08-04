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
        defaultMessage="THIS VIEW"
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
        defaultMessage="THIS VIEW"
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
        defaultMessage="THIS VIEW"
      />
    </div>
  </div>
);

export class MapViewButton extends Component {
  handleOnClick = () => {
    const icon = this.getIcon();

    if (icon === SELECTED_ICON) {
      this.props.setAllButtonsDefault();
      this.props.handleCancel();
    } else if (icon === DEFAULT_ICON) {
      this.props.setMapViewButtonSelected();
      this.props.setMapView();
    }
  };

  getIcon() {
    const { toolbarIcons: { mapView: icon } } = this.props;

    switch (icon) {
      case "SELECTED":
        return SELECTED_ICON;

      case "INACTIVE":
        return INACTIVE_ICON;

      default:
        return DEFAULT_ICON;
    }
  }

  render() {
    const icon = this.getIcon();

    return (
      <div className={styles.drawButtonGeneral} onClick={this.handleOnClick}>
        {icon}
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
