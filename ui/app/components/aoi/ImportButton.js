import React, { Component } from "react";
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
    <div className={styles.buttonName}>IMPORT</div>
  </div>
);

const INACTIVE_ICON = (
  <div>
    <i className={"material-icons " + styles.inactiveButton}>file_upload</i>
    <div className={styles.buttonName + " " + styles.buttonNameInactive}>
      IMPORT
    </div>
  </div>
);

const SELECTED_ICON = (
  <div>
    <i className={"material-icons " + styles.selectedButton}>clear</i>
    <div className={styles.buttonName}>IMPORT</div>
  </div>
);

export class ImportButton extends Component {
  state = {
    icon: DEFAULT_ICON
  };

  componentWillReceiveProps(nextProps) {
    // TODO state is totally unnecessary here
    //If the button has been selected update the button state
    if (nextProps.toolbarIcons.import === "SELECTED") {
      this.setState({ icon: SELECTED_ICON });
    }
    //If the button has been de-selected update the button state
    if (nextProps.toolbarIcons.import === "DEFAULT") {
      this.setState({ icon: DEFAULT_ICON });
    }
    //If the button has been set as inactive update the state
    if (nextProps.toolbarIcons.import === "INACTIVE") {
      this.setState({ icon: INACTIVE_ICON });
    }
  }

  handleOnClick = () => {
    if (this.state.icon === SELECTED_ICON) {
      this.props.setAllButtonsDefault();
      this.props.setImportModalState(false);
      this.props.handleCancel();
    } else if (this.state.icon === DEFAULT_ICON) {
      this.props.setImportButtonSelected();
      this.props.setImportModalState(true);
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
