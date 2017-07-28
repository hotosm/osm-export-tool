import React, { Component } from "react";
import { connect } from "react-redux";

import styles from "../../styles/aoi/DropZone.css";
import {
  setAllButtonsDefault,
  resetGeoJSONFile
} from "../../actions/aoi/mapToolActions";
import { PopupBox } from "./PopupBox";

export class DropZoneError extends Component {
  state = {
    showErrorMessage: false,
    errorMessage: null
  };

  componentWillReceiveProps(nextProps) {
    if (nextProps.importGeom.error !== this.props.importGeom.error) {
      if (nextProps.importGeom.error) {
        this.props.setAllButtonsDefault();
        this.setState({
          showErrorMessage: true,
          errorMessage: nextProps.importGeom.error
        });
      }
    }
  }

  handleErrorClear = () => {
    this.setState({ showErrorMessage: false });
    this.props.resetGeoJSONFile();
  };

  render() {
    return (
      <PopupBox
        show={this.state.showErrorMessage}
        title="Error"
        onExit={this.handleErrorClear}
      >
        <div className={styles.fileError}>
          {this.state.errorMessage}
        </div>
      </PopupBox>
    );
  }
}

function mapStateToProps(state) {
  return {
    importGeom: state.importGeom
  };
}

export default connect(mapStateToProps, {
  resetGeoJSONFile,
  setAllButtonsDefault
})(DropZoneError);
