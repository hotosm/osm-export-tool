import React, {Component} from 'react';
import {connect} from 'react-redux';
import styles from '../styles/DrawAOIToolbar.css';
import {updateMode} from '../actions/exportsActions.js';
import {setImportButtonSelected, setAllButtonsDefault, setImportModalState} from '../actions/mapToolActions';

export class ImportButton extends Component {

    constructor(props) {
        super(props);
        this.handleOnClick = this.handleOnClick.bind(this);
        this.state = {
            icon: DEFAULT_ICON,
        }
    }

    componentWillReceiveProps(nextProps) {
        //If the button has been selected update the button state
        if(nextProps.toolbarIcons.import == 'SELECTED') {
            this.setState({icon: SELECTED_ICON});
        }
        //If the button has been de-selected update the button state
        if(nextProps.toolbarIcons.import == 'DEFAULT') {
            this.setState({icon: DEFAULT_ICON});
        }
        //If the button has been set as inactive update the state
        if(nextProps.toolbarIcons.import == 'INACTIVE') {
            this.setState({icon: INACTIVE_ICON});
        }
    }

    handleOnClick() {
        if(this.state.icon == SELECTED_ICON) {
            this.props.setAllButtonsDefault();
            this.props.setImportModalState(false);
            this.props.handleCancel();
        }
        else if(this.state.icon == DEFAULT_ICON) {
            this.props.setImportButtonSelected();
            this.props.setImportModalState(true);
        }
    }

    render() {
        return (
            <button className={styles.drawButtonGeneral} onClick={this.handleOnClick}>
                {this.state.icon}
            </button>
        )
    }
}

const DEFAULT_ICON = <div>
                        <i className={"material-icons " + styles.defaultButton}>file_upload</i>
                        <div className={styles.buttonName}>IMPORT</div>
                    </div>

const INACTIVE_ICON = <div>
                        <i className={"material-icons " + styles.inactiveButton}>file_upload</i>
                        <div className={styles.buttonName + ' ' + styles.buttonNameInactive}>IMPORT</div>
                    </div>

const SELECTED_ICON =<div>
                        <i className={"material-icons " + styles.selectedButton}>clear</i>
                        <div className={styles.buttonName}>IMPORT</div>
                    </div>

function mapStateToProps(state) {
    return {
        toolbarIcons: state.toolbarIcons,
        mode: state.mode,
        showImportModal: state.showImportModal,
    };
}

function mapDispatchToProps(dispatch) {
    return {
        updateMode: (newMode) => {
            dispatch(updateMode(newMode));
        },
        setImportButtonSelected: () => {
            dispatch(setImportButtonSelected());
        },
        setAllButtonsDefault: () => {
            dispatch(setAllButtonsDefault());
        },
        setImportModalState: (visibility) => {
            dispatch(setImportModalState(visibility));
        }
    }
}

export default connect(
    mapStateToProps,
    mapDispatchToProps
)(ImportButton);
