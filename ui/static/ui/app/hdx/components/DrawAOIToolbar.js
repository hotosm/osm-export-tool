import React, {Component} from 'react';
import {connect} from 'react-redux';
import styles from '../styles/DrawAOIToolbar.css';
import DrawBoxButton from './DrawBoxButton';
import DrawFreeButton from './DrawFreeButton';
import MapViewButton from './MapViewButton';
import ImportButton from './ImportButton';
import {setAllButtonsDefault} from '../actions/mapToolActions';


export class DrawAOIToolbar extends Component {

    constructor(props) {
        super(props);
    }

    componentDidMount() {
        this.props.setAllButtonsDefault();
    }

    render() {
        return (
            <div>
                <div className={styles.drawButtonsContainer}>
                    <div className={styles.drawButtonsTitle}><strong>TOOLS</strong></div>
                    <DrawBoxButton handleCancel={(sender) => this.props.handleCancel(sender)}/>
                    <DrawFreeButton handleCancel={(sender) => this.props.handleCancel(sender)}/>
                    <MapViewButton handleCancel={(sender) => this.props.handleCancel(sender)}
                                    setMapView={this.props.setMapView}/>
                    <ImportButton handleCancel={(sender) => this.props.handleCancel(sender)}/>
                </div>
            </div>
        )
    }
}

function mapDispatchToProps(dispatch) {
    return {
        setAllButtonsDefault: () => {
            dispatch(setAllButtonsDefault());
        },
    };
}

export default connect(
    null,
    mapDispatchToProps,
)(DrawAOIToolbar);
