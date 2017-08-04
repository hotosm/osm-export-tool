import React, { Component } from "react";
import { FormattedMessage } from "react-intl";
import { connect } from "react-redux";

import styles from "../../styles/aoi/DrawAOIToolbar.css";
import { updateMode } from "../../actions/exports";
import {
  setImportButtonSelected,
  setAllButtonsDefault,
  setImportModalState
} from "../../actions/aoi/mapToolActions";

const DEFAULT_ICON = (
  <div>
    <i className={"material-icons " + styles.defaultButton}>file_upload</i>
    <div className={styles.buttonName}>
      <FormattedMessage id="ui.draw.import" defaultMessage="IMPORT" />
    </div>
  </div>
);

const INACTIVE_ICON = (
  <div>
    <i className={"material-icons " + styles.inactiveButton}>file_upload</i>
    <div className={styles.buttonName + " " + styles.buttonNameInactive}>
      <FormattedMessage id="ui.draw.import" defaultMessage="IMPORT" />
    </div>
  </div>
);

const SELECTED_ICON = (
  <div>
    <i className={"material-icons " + styles.selectedButton}>clear</i>
    <div className={styles.buttonName}>
      <FormattedMessage id="ui.draw.import" defaultMessage="IMPORT" />
    </div>
  </div>
);

export class ImportButton extends Component {
  handleOnClick = () => {
    const icon = this.getIcon();

    if (icon === SELECTED_ICON) {
      this.props.setAllButtonsDefault();
      this.props.setImportModalState(false);
      this.props.handleCancel();
    } else if (icon === DEFAULT_ICON) {
      this.props.setImportButtonSelected();
      this.props.setImportModalState(true);
    }
  };

  getIcon() {
    const { toolbarIcons: { import: icon } } = this.props;

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
    toolbarIcons: state.toolbarIcons,
    mode: state.mode,
    showImportModal: state.showImportModal
  };
}

export default connect(mapStateToProps, {
  setAllButtonsDefault,
  setImportButtonSelected,
  setImportModalState,
  updateMode
})(ImportButton);
