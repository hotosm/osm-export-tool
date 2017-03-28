import React, {Component} from 'react';
import ol from 'openlayers';
import styles from '../styles/CreateExport.css';

const WGS84 = 'EPSG:4326';
const WEB_MERCATOR = 'EPSG:3857';
const isEqual = require('lodash/isEqual');

export class MapListView extends Component {

    constructor(props) {
        super(props)
        this.handleResetMap = this.handleResetMap.bind(this);
    }

    componentDidMount() {
        this._initializeOpenLayers();
    }

    componentWillReceiveProps(nextProps) {
        // Check if the reset map button has been clicked
        if(this.props.resetMap.click != nextProps.resetMap.click) {
            this.handleResetMap();
        }
    }

    handleResetMap() {
        let worldExtent = ol.proj.transformExtent([-180,-90,180,90], WGS84, WEB_MERCATOR)
        this._map.getView().fit(worldExtent, this._map.getSize());
    }

    _initializeOpenLayers() {

        const scaleStyle = {
            background: 'white',
        };


        this._map = new ol.Map({
            controls: [
                new ol.control.ScaleLine({
                    className: styles.olScaleLine,
                }),
                new ol.control.Attribution({
                    collapsible: false,
                    collapsed: false,
                }),
                new ol.control.Zoom({
                    className: styles.olZoom
                }),
                new ol.control.ZoomExtent({
                    className: styles.olZoomToExtent,
                    extent: [-14251567.50789682, -10584983.780136958, 14251787.50789682, 10584983.780136958]
                }),
            ],
            interactions: ol.interaction.defaults({
                keyboard: false,
                altShiftDragRotate: false,
                pinchRotate: false
            }),
            layers: [
                // Order matters here
                new ol.layer.Tile({
                    source: new ol.source.OSM()
                }),
            ],
            target: 'map',
            view: new ol.View({
                projection: "EPSG:3857",
                center: [110, 0],
                zoom: 2.5,
                minZoom: 2.5,
                maxZoom: 22,
            })
        });

    }


    render() {

        const mapStyle = {};

        let buttonClass = `${styles.draw || ''} ol-unselectable ol-control`

        return (
            <div>
                <div id="map" className={styles.map}  style={mapStyle} ref="olmap">
                </div>
            </div>
        );
    }
}

MapListView.propTypes = {
    resetMap: React.PropTypes.object
}

export default MapListView;

ol.control.ZoomExtent = function(opt_option) {
    let options = opt_option ? opt_option : {};
    options.className = options.className != undefined ? options.className : ''

    let button = document.createElement('button');
    let icon = document.createElement('i');
    icon.className = 'fa fa-globe';
    button.appendChild(icon);
    let this_ = this;

    this.zoomer = () => {
        const extent = !options.extent ? view.getProjection.getExtent() : options.extent;
        const map = this_.getMap();
        const view = map.getView();
        const size = map.getSize();
        view.fit(options.extent, size);
    }

    button.addEventListener('click', this_.zoomer, false);
    button.addEventListener('touchstart', this_.zoomer, false);
    let element = document.createElement('div');
    element.className = options.className + ' ol-unselectable ol-control';
    element.appendChild(button);

    ol.control.Control.call(this, {
        element: element,
        target: options.target
    });
}
ol.inherits(ol.control.ZoomExtent, ol.control.Control);

