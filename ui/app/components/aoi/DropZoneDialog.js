import React, { Component } from "react";
import Dropzone from "react-dropzone";
import { connect } from "react-redux";

import styles from "../../styles/aoi/DropZone.css";
import {
  setAllButtonsDefault,
  setImportModalState,
  processGeoJSONFile
} from "../../actions/aoi/mapToolActions";
import { PopupBox } from "./PopupBox";

export class DropZoneDialog extends Component {
  onDrop = acceptedFiles => {
    if (acceptedFiles.length === 1) {
      const file = acceptedFiles[0];
      this.props.setImportModalState(false);
      this.props.processGeoJSONFile(file);
    }
  };

  onOpenClick = () => {
    this.dropzone.open();
  };

  handleClear = () => {
    this.props.setImportModalState(false);
    this.props.setAllButtonsDefault();
  };

  render() {
    return (
      <PopupBox
        show={this.props.showImportModal}
        title="Import AOI"
        onExit={this.handleClear}
      >
        <Dropzone
          onDrop={this.onDrop}
          multiple={false}
          className={styles.dropZone}
          ref={node => {
            this.dropzone = node;
          }}
          disableClick={true}
          maxSize={5000000}
        >
          <div className={styles.dropZoneText}>
            <span>
              <strong>GeoJSON</strong> file in{" "}
              <strong>geographic coordinates (WGS84), 5 MB</strong> max,<br />Drag
              and drop or<br />
            </span>
            <button
              type="button"
              onClick={this.onOpenClick}
              className={styles.dropZoneImportButton}
            >
              <i className={"material-icons"}>file_upload</i>Select A File
            </button>
          </div>
        </Dropzone>
      </PopupBox>
    );
  }
}

function mapStateToProps(state) {
  return {
    showImportModal: state.showImportModal
  };
}

export default connect(mapStateToProps, {
  processGeoJSONFile,
  setAllButtonsDefault,
  setImportModalState
})(DropZoneDialog);
