import React, {Component} from 'react';
import {connect} from 'react-redux';
import styles from '../styles/AoiInfobar.css';
import {toggleZoomToSelection, clickZoomToSelection, toggleResetMap, clickResetMap} from '../actions/AoiInfobarActions.js';
import {PopupBox} from './PopupBox.js';

export const NO_SELECTION_ICON = 'warning';
export const POLYGON_ICON = 'crop_square';
export const POINT_ICON = 'room';

const isEqual = require('lodash/isEqual');

export class AoiInfobar extends Component {

    constructor(props) {
        super(props)
        this.dispatchZoomToSelection = this.dispatchZoomToSelection.bind(this);
        this.handleAoiInfo = this.handleAoiInfo.bind(this);
        // this.handleInfoClick = this.handleInfoClick.bind(this);

        this.state = {
            aoiDescription: '',
            aoiTitle: '',
            geometryIcon: NO_SELECTION_ICON,
            showInfoPopup: false,
            showAoiInfobar: false,
        }
    }

    componentWillReceiveProps(nextProps) {
        if(!isEqual(nextProps.aoiInfo.geojson, this.props.aoiInfo.geojson)) {
            this.handleAoiInfo(nextProps.aoiInfo);
        }
    }

    handleAoiInfo(aoiInfo) {
        if(!isEqual(aoiInfo.geojson, {})) {
            if(aoiInfo.geomType == 'Point') {
            this.setState({geometryIcon: POINT_ICON});
            }
            else if(aoiInfo.geomType == 'Polygon') {
                this.setState({geometryIcon: POLYGON_ICON});
            }
            this.setState({aoiTitle: aoiInfo.title});
            this.setState({aoiDescription: aoiInfo.description});
            this.setState({showAoiInfobar: true});
        }
        else {
            this.setState({showAoiInfobar: false});
            this.setState({geometryIcon: NO_SELECTION_ICON});
            this.setState({aoiTitle: ''});
            this.setState({aoiDescription: 'No AOI Set'});    
        }
    }

    // handleInfoClick() {
    //     this.setState({showInfoPopup: true})
    // }

    dispatchZoomToSelection() {
        //If the zoom button is active dispatch the click
        if(!this.props.zoomToSelection.disabled){
            this.props.clickZoomToSelection();
        }
    }

    render() {
        return (
            <div>
                <div className={styles.aoiInfoWrapper}>
                    {this.state.showAoiInfobar ? 
                    <div className={styles.aoiInfobar}>
                        <div className={styles.topBar}>
                            <span className={styles.aoiInfoTitle}><strong>Area Of Interest (AOI)</strong></span>
                            <button className={styles.simpleButton + ' ' + styles.activeButton} onClick={this.dispatchZoomToSelection}>
                                <i className={"fa fa-search-plus"}></i> ZOOM TO SELECTION
                            </button>
                        </div>
                        <div className={styles.detailBar}>
                            <i className={"material-icons " + styles.geometryIcon}>
                                    {this.state.geometryIcon}
                            </i>
                            <div className={styles.detailText}>
                                <div className={styles.aoiTitle}>
                                    <strong>{this.state.aoiTitle}</strong>
                                    {/*{this.state.geometryIcon != NO_SELECTION_ICON ? 
                                        <button className={styles.aoiInfo} onClick={this.handleInfoClick}>
                                            <i className={"material-icons"} style={{fontSize: '15px', color: '#4598bf'}}>info</i>
                                        </button>
                                    : null}*/}
                                </div>
                                <div className={styles.aoiDescription}>
                                    {this.state.aoiDescription}
                                </div>
                            </div>
                        </div>   
                    </div>
                    : null}
                </div>
                {/*<PopupBox show={this.state.showInfoPopup} title='AOI Info' onExit={() => {this.setState({showInfoPopup: false})}}>
                    <p> AOI Geojson </p>
                    <div style={{overflowY: 'scroll', maxHeight: '430px'}}>{JSON.stringify(this.props.aoiInfo.geojson, undefined, 2)}</div>
                </PopupBox>*/}
            </div>
        )
    }
}

AoiInfobar.propTypes = {
    aoiInfo: React.PropTypes.object,
    zoomToSelection: React.PropTypes.object,
    clickZoomToSelection: React.PropTypes.func,
}

function mapStateToProps(state) {
    return {
        aoiInfo: state.aoiInfo,
        zoomToSelection: state.zoomToSelection,
    }
}

function mapDispatchToProps(dispatch) {
    return {
        
        clickZoomToSelection: () => {
            dispatch(clickZoomToSelection());
        },
    }
}

export default connect(
    mapStateToProps,
    mapDispatchToProps
)(AoiInfobar)
