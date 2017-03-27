import React, {Component} from 'react';
import {connect} from 'react-redux';
import styles from '../styles/DropZone.css';
import {setImportButtonSelected, setAllButtonsDefault, setImportModalState, processGeoJSONFile, resetGeoJSONFile} from '../actions/mapToolActions';
import {PopupBox} from './PopupBox.js';
const Dropzone = require('react-dropzone');

export class DropZoneDialog extends Component {

    constructor(props) {
        super(props);
        this.onDrop = this.onDrop.bind(this);
        this.onOpenClick = this.onOpenClick.bind(this);
        this.handleClear = this.handleClear.bind(this);
    }

    onDrop(acceptedFiles) {
        if(acceptedFiles.length == 1) {
            const file = acceptedFiles[0];
            this.props.setImportModalState(false);
            this.props.processGeoJSONFile(file);
        }
    }

    onOpenClick() {
        this.dropzone.open();
    }

    handleClear() {
        this.props.setImportModalState(false);
        this.props.setAllButtonsDefault();
    }
    render() {

        return (
            <PopupBox 
                show={this.props.showImportModal}
                title="Import AOI"
                onExit={this.handleClear}>
                <Dropzone onDrop={this.onDrop} 
                            multiple={false} 
                            className={styles.dropZone}
                            ref={(node) => {this.dropzone = node;}} 
                            disableClick={true}
                            maxSize={28000000}>
                        <div className={styles.dropZoneText}>
                        <span><strong>GeoJSON</strong> format only, <strong>26MB</strong> max,<br/>Drag and drop or<br/></span>
                        <button onClick={this.onOpenClick} className={styles.dropZoneImportButton}><i className={"material-icons"}>file_upload</i>Select A File</button>
                        </div>
                    </Dropzone>
            </PopupBox>
        )
    }
}

function mapStateToProps(state) {
    return {
        showImportModal: state.showImportModal,
    };
}


function mapDispatchToProps(dispatch) {
    return {
        setAllButtonsDefault: () => {
            dispatch(setAllButtonsDefault());
        },
        setImportModalState: (visibility) => {
            dispatch(setImportModalState(visibility));
        },
        processGeoJSONFile: (file) => {
            dispatch(processGeoJSONFile(file));
        },
    }
}

export default connect(
    mapStateToProps,
    mapDispatchToProps
)(DropZoneDialog);
