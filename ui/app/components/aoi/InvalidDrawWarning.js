import React, {Component} from 'react';
import {connect} from 'react-redux';
import styles from '../../styles/aoi/InvalidDrawWarning.css';

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
                <span>{this.props.msg}</span>
            </div>
        )
    }
}

function mapStateToProps(state) {
    return {
        show: (state.invalidDrawWarning !== ""),
        msg: state.invalidDrawWarning
    };
}

function mapDispatchToProps(dispatch) {
    return {}
}

export default connect(
    mapStateToProps,
    mapDispatchToProps
)(InvalidDrawWarning);
