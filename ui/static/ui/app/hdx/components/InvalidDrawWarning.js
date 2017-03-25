import React, {Component} from 'react';
import {connect} from 'react-redux';
import styles from '../styles/InvalidDrawWarning.css';
import {showInvalidDrawWarning, hideInvalidDrawWarning} from '../actions/drawToolBarActions.js';

export class InvalidDrawWarning extends Component {

    constructor(props) {
        super(props);
        this.state = {
            visibilityClass: styles.hidden,
        }
    }

    componentWillReceiveProps(nextProps){
        if(nextProps.show != this.props.show) {
            if(nextProps.show) {
                this.setState({visibilityClass: styles.visible});
            }
            else {
                this.setState({visibilityClass: styles.hidden});
            }
        }
    }

    render() {

        return (
            <div className={styles.invalidWarning + " " + this.state.visibilityClass}>
                <span>You drew an invalid bounding box, please redraw.</span>
            </div>
        )
    }
}

function mapStateToProps(state) {
    return {
        show: state.showInvalidDrawWarning
    };
}

function mapDispatchToProps(dispatch) {
    return {
        hideInvalidDrawWarning: () => {
            dispatch(hideInvalidDrawWarning());
        },
        showInvalidDrawWarning: () => {
            dispatch(showInvalidDrawWarning());
        },
    }
}

export default connect(
    mapStateToProps,
    mapDispatchToProps
)(InvalidDrawWarning);
