import React, {Component} from 'react';
import {connect} from 'react-redux';
import styles from '../styles/DropZone.css';
import {setAllButtonsDefault, resetGeoJSONFile} from '../actions/mapToolActions';
import {PopupBox} from './PopupBox';

export class DropZoneError extends Component {

    constructor(props) {
        super(props);
        this.handleErrorClear = this.handleErrorClear.bind(this);
        this.state = {
            showErrorMessage: false,
            errorMessage: null,
        }
    }

    componentWillReceiveProps(nextProps) {
        if(nextProps.importGeom.error != this.props.importGeom.error) {
            if(nextProps.importGeom.error) {
                this.props.setAllButtonsDefault();
                this.setState({showErrorMessage: true, errorMessage: nextProps.importGeom.error});
            }
        }
    }

    handleErrorClear() {
        this.setState({showErrorMessage: false});
        this.props.resetGeoJSONFile();
    }

    render() {

        return (
            <PopupBox
                show={this.state.showErrorMessage}
                title="Error"
                onExit={this.handleErrorClear}>
                <div className={styles.fileError}>
                    {this.state.errorMessage}
                </div>
            </PopupBox>
        )
    }
}

function mapStateToProps(state) {
    return {
        importGeom: state.importGeom,
    };
}


function mapDispatchToProps(dispatch) {
    return {
        setAllButtonsDefault: () => {
            dispatch(setAllButtonsDefault());
        },
        resetGeoJSONFile: (file) => {
            dispatch(resetGeoJSONFile());
        },
    }
}

export default connect(
    mapStateToProps,
    mapDispatchToProps
)(DropZoneError);
