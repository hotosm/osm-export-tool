import React, {Component} from 'react';
import {connect} from 'react-redux';
import ol from 'openlayers';
import styles from '../styles/CreateExport.css';
import {Toolbar, ToolbarGroup, ToolbarSeparator,ToolbarTitle} from 'material-ui/Toolbar';
import AoiInfobar from './AoiInfobar.js';
import SearchAOIToolbar from './SearchAOIToolbar.js';
import DrawAOIToolbar from './DrawAOIToolbar.js';
import InvalidDrawWarning from './InvalidDrawWarning.js';
import DropZone from './DropZone.js';
import {updateMode, updateAoiInfo, clearAoiInfo, stepperNextDisabled, stepperNextEnabled} from '../actions/exportsActions.js';
import {hideInvalidDrawWarning, showInvalidDrawWarning} from '../actions/drawToolBarActions.js';

export const MODE_DRAW_BBOX = 'MODE_DRAW_BBOX';
export const MODE_NORMAL = 'MODE_NORMAL';
export const MODE_DRAW_FREE = 'MODE_DRAW_FREE';
const WGS84 = 'EPSG:4326';
const WEB_MERCATOR = 'EPSG:3857';
const jsts = require('jsts');
const isEqual = require('lodash/isEqual');

const GEOJSON_FORMAT = new ol.format.GeoJSON();

export class ExportAOI extends Component {

    constructor(props) {
        super(props)
        this._handleDrawStart = this._handleDrawStart.bind(this);
        this._handleDrawEnd = this._handleDrawEnd.bind(this);
        this.handleCancel = this.handleCancel.bind(this);
        this.handleZoomToSelection = this.handleZoomToSelection.bind(this);
        this.handleResetMap = this.handleResetMap.bind(this);
        this.handleSearch = this.handleSearch.bind(this);
        this.setMapView = this.setMapView.bind(this);
        this.handleGeoJSONUpload = this.handleGeoJSONUpload.bind(this);
    }

    getFeature (geojson) {
        switch (geojson.type) {
            case 'FeatureCollection':
                return GEOJSON_FORMAT.readFeature(geojson.features[0], {
                    dataProjection: WGS84,
                    featureProjection: WEB_MERCATOR
                });

            case 'Feature':
                return GEOJSON_FORMAT.readFeature(geojson, {
                    dataProjection: WGS84,
                    featureProjection: WEB_MERCATOR
                });

            default:
                const geometry = GEOJSON_FORMAT.readGeometry(geojson, {
                    dataProjection: WGS84,
                    featureProjection: WEB_MERCATOR
                });

                console.log('geometry:', geometry);
                return new ol.Feature({
                    geometry: GEOJSON_FORMAT.readGeometry(geojson, {
                        dataProjection: WGS84,
                        featureProjection: WEB_MERCATOR
                    })
                });
        }
    }

    componentDidMount() {
        const { aoiInfo: { geojson } } = this.props;

        this._initializeOpenLayers();
        this._updateInteractions();

        if (geojson != null && Object.keys(geojson).length > 0) {
            const feature = this.getFeature(geojson);
            this._drawLayer.getSource().addFeature(feature);
            this.handleZoomToSelection(serialize(feature.getGeometry().getExtent()));
            this.props.setNextEnabled();
        }
    }

    componentDidUpdate(prevProps, prevState) {
        if (!isEqual(prevProps.aoiInfo.geojson, this.props.aoiInfo.geojson)) {
            // remove existing features
            this._clearDraw();

            const feature = this.getFeature(this.props.aoiInfo.geojson);
            this._drawLayer.getSource().addFeature(feature);
            this.handleZoomToSelection(serialize(feature.getGeometry().getExtent()));
            this.props.setNextEnabled();
        }
    }

    componentWillReceiveProps(nextProps) {
        // Check if the map mode has changed (DRAW or NORMAL)
        if(this.props.mode != nextProps.mode) {
            this._updateInteractions(nextProps.mode);
        }
        if(this.props.zoomToSelection.click != nextProps.zoomToSelection.click) {
            this.handleZoomToSelection(nextProps.aoiInfo.geojson.features[0].bbox);
        }
        // Check if the reset map button has been clicked
        if(this.props.resetMap.click != nextProps.resetMap.click) {
            this.handleResetMap();
        }
        if(nextProps.importGeom.processed && !this.props.importGeom.processed) {
            this.handleGeoJSONUpload(nextProps.importGeom.geojson);
        }
    }

    handleCancel(sender) {
        this.props.hideInvalidDrawWarning();
        if(this.props.mode != MODE_NORMAL) {
            this.props.updateMode(MODE_NORMAL);
        }
        this._clearDraw();
        this.props.clearAoiInfo();
        this.props.setNextDisabled();
    }

    handleZoomToSelection(bbox) {
        this._map.getView().fit(
            ol.proj.transformExtent(bbox, WGS84, WEB_MERCATOR),
            this._map.getSize()
        );
    }

    handleResetMap() {
        let worldExtent = ol.proj.transformExtent([-180,-90,180,90], WGS84, WEB_MERCATOR)
        this._map.getView().fit(worldExtent, this._map.getSize());
    }

    handleSearch(result) {
        const unformatted_bbox = result.bbox;
        const formatted_bbox = [unformatted_bbox.west, unformatted_bbox.south, unformatted_bbox.east, unformatted_bbox.north]
        this._clearDraw();
        this.props.hideInvalidDrawWarning();
        const bbox = formatted_bbox.map(truncate);
        const mercBbox = ol.proj.transformExtent(bbox, WGS84, WEB_MERCATOR);
        const geom = new ol.geom.Polygon.fromExtent(mercBbox);
        const geojson = createGeoJSON(geom);
        const bboxFeature = new ol.Feature({
            geometry: geom
        });
        this._drawLayer.getSource().addFeature(bboxFeature);
        let description = '';
        description = description + (result.countryName ? result.countryName : '');
        description = description + (result.adminName1 ? ', ' + result.adminName1 : '');
        description = description + (result.adminName2 ? ', ' + result.adminName2 : '');


        this.props.updateAoiInfo(geojson, 'Polygon', result.name, description);
        this.props.setNextEnabled();
        this.handleZoomToSelection(bbox);
    }

    handleGeoJSONUpload(geojson) {
        this.props.updateAoiInfo(geojson, 'Polygon', 'Custom Polygon', 'Import');
    }

    setMapView() {
        this._clearDraw();
        const extent = this._map.getView().calculateExtent(this._map.getSize());
        const geom = new ol.geom.Polygon.fromExtent(extent);
        const geojson = createGeoJSON(geom);
        const bboxFeature = new ol.Feature({
            geometry: geom
        });
        const bbox = serialize(extent)
        this._drawLayer.getSource().addFeature(bboxFeature);
        this.props.updateAoiInfo(geojson, 'Polygon', 'Custom Polygon', 'Map View');
        this.props.setNextEnabled();
    }


    _activateDrawInteraction(mode) {
        if(mode == MODE_DRAW_BBOX) {
            this._drawFreeInteraction.setActive(false);
            this._drawBoxInteraction.setActive(true);
        }
        else if(mode == MODE_DRAW_FREE) {
            this._drawBoxInteraction.setActive(false);
            this._drawFreeInteraction.setActive(true);
        }
    }

    _clearDraw() {
        this._drawLayer.getSource().clear();
    }

    _deactivateDrawInteraction() {
        this._drawBoxInteraction.setActive(false);
        this._drawFreeInteraction.setActive(false);
    }

    _handleDrawEnd(event) {
        // get the drawn bounding box
        const geometry = event.feature.getGeometry();
        const geojson = createGeoJSON(geometry);
        if (this.props.mode == MODE_DRAW_FREE) {
            let drawFeature = new ol.Feature({
                geometry: geometry
            });
            this._drawLayer.getSource().addFeature(drawFeature);

            if(isGeoJSONValid(geojson)) {
                this.props.updateAoiInfo(geojson, 'Polygon', 'Custom Polygon', 'Draw');
                this.props.setNextEnabled();
            }
            else {
                this.props.showInvalidDrawWarning();
            }
        }
        else if (this.props.mode == MODE_DRAW_BBOX) {
            const bbox = serialize(geometry.getExtent());
            this.props.updateAoiInfo(geojson, 'Polygon', 'Custom Polygon', 'Box');
            this.props.setNextEnabled();
        }
        // exit drawing mode
        this.props.updateMode('MODE_NORMAL');
    }

    _handleDrawStart() {
        this._clearDraw();
    }


    _initializeOpenLayers() {

        const scaleStyle = {
            background: 'white',
        };

        this._drawLayer = generateDrawLayer();
        this._drawBoxInteraction = _generateDrawBoxInteraction(this._drawLayer);
        this._drawBoxInteraction.on('drawstart', this._handleDrawStart);
        this._drawBoxInteraction.on('drawend', this._handleDrawEnd);

        this._drawFreeInteraction = _generateDrawFreeInteraction(this._drawLayer);
        this._drawFreeInteraction.on('drawstart', this._handleDrawStart);
        this._drawFreeInteraction.on('drawend', this._handleDrawEnd);

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

        this._map.addInteraction(this._drawBoxInteraction);
        this._map.addInteraction(this._drawFreeInteraction);
        this._map.addLayer(this._drawLayer);
    }


    render() {

        const mapStyle = {};

        let buttonClass = `${styles.draw || ''} ol-unselectable ol-control`

        return (
            <div>
                <div id="map" className={styles.map}  style={mapStyle} ref="olmap">
                    <AoiInfobar />
                    <SearchAOIToolbar 
                        handleSearch={(result) => this.handleSearch(result)}
                        handleCancel={(sender) => this.handleCancel(sender)}/>
                    <DrawAOIToolbar handleCancel={(sender) => this.handleCancel(sender)}
                                    setMapView={this.setMapView}/>
                    <InvalidDrawWarning />
                    <DropZone/>
                </div>
            </div>
        );
    }

    _updateInteractions(mode) {

        switch (mode) {
            case MODE_DRAW_BBOX:
                this._activateDrawInteraction(MODE_DRAW_BBOX);
                break
            case MODE_DRAW_FREE:
                this._activateDrawInteraction(MODE_DRAW_FREE);
                break
            case MODE_NORMAL:
                this._deactivateDrawInteraction();
                break
        }
    }
}

ExportAOI.propTypes = {
    aoiInfo: React.PropTypes.object,
    mode: React.PropTypes.string,
    zoomToSelection: React.PropTypes.object,
    resetMap: React.PropTypes.object,
    importGeom: React.PropTypes.object,
    drawerOpen: React.PropTypes.bool,
    updateMode: React.PropTypes.func,
    hideInvalidDrawWarning: React.PropTypes.func,
    showInvalidDrawWarning: React.PropTypes.func,
    updateAoiInfo: React.PropTypes.func,
    clearAoiInfo: React.PropTypes.func,
    setNextDisabled: React.PropTypes.func,
    setNextEnabled: React.PropTypes.func
}


function mapStateToProps(state) {
    return {
        aoiInfo: state.aoiInfo,
        mode: state.mode,
        zoomToSelection: state.zoomToSelection,
        resetMap: state.resetMap,
        importGeom: state.importGeom,
        drawerOpen: state.drawerOpen,
    };
}

function mapDispatchToProps(dispatch) {
    return {
        updateMode: (newMode) => {
            dispatch(updateMode(newMode));
        },
        hideInvalidDrawWarning: () => {
            dispatch(hideInvalidDrawWarning());
        },
        showInvalidDrawWarning: () => {
            dispatch(showInvalidDrawWarning());
        },
        updateAoiInfo: (geojson, geomType, title, description) => {
            dispatch(updateAoiInfo(geojson, geomType, title, description));
        },
        clearAoiInfo: () => {
            dispatch(clearAoiInfo());
        },
        setNextDisabled: () => {
            dispatch(stepperNextDisabled());
        },
        setNextEnabled: () => {
            dispatch(stepperNextEnabled());
        },
    }
}

export default connect(
    mapStateToProps,
    mapDispatchToProps
)(ExportAOI);



function generateDrawLayer() {
    return new ol.layer.Vector({
        source: new ol.source.Vector({
            wrapX: false
        }),
        style: new ol.style.Style({
            fill: new ol.style.Fill({
                color: 'hsla(202, 70%, 50%, .35)'
            }),
            stroke: new ol.style.Stroke({
                color: 'hsla(202, 70%, 50%, .7)',
                width: 1,
                lineDash: [5, 5]
            })
        })
    })
}

function _generateDrawBoxInteraction(drawLayer) {
    const draw = new ol.interaction.Draw({
        source: drawLayer.getSource(),
        maxPoints: 2,
        type: 'LineString',
        geometryFunction(coordinates, geometry) {
            geometry = geometry || new ol.geom.Polygon(null)
            const [[x1, y1], [x2, y2]] = coordinates
            geometry.setCoordinates([[[x1, y1], [x1, y2], [x2, y2], [x2, y1], [x1, y1]]])
            return geometry
        },
        style: new ol.style.Style({
            image: new ol.style.RegularShape({
                stroke: new ol.style.Stroke({
                    color: 'black',
                    width: 1
                }),
                points: 4,
                radius: 15,
                radius2: 0,
                angle: 0
            }),
            fill: new ol.style.Fill({
                color: 'hsla(202, 70%, 50%, .6)'
            }),
            stroke: new ol.style.Stroke({
                color: 'hsl(202, 70%, 50%)',
                width: 1,
                lineDash: [5, 5]
            })
        })
    })
    draw.setActive(false)
    return draw
}

function _generateDrawFreeInteraction(drawLayer) {
    const draw = new ol.interaction.Draw({
        source: drawLayer.getSource(),
        type: 'Polygon',
        freehand: true,
        style: new ol.style.Style({
            image: new ol.style.RegularShape({
                stroke: new ol.style.Stroke({
                    color: 'black',
                    width: 1
                }),
                points: 4,
                radius: 15,
                radius2: 0,
                angle: 0
            }),
            fill: new ol.style.Fill({
                color: 'hsla(202, 70%, 50%, .6)'
            }),
            stroke: new ol.style.Stroke({
                color: 'hsl(202, 70%, 50%)',
                width: 1,
                lineDash: [5, 5]
            })
        })
    })
    draw.setActive(false)
    return draw
}



function truncate(number) {
    return Math.round(number * 100) / 100
}

function unwrapPoint([x, y]) {
    return [
        x > 0 ? Math.min(180, x) : Math.max(-180, x),
        y
    ]
}

function featureToBbox(feature) {
    const geometry = GEOJSON_FORMAT.readGeometry(feature.geometry, {featureProjection: WEB_MERCATOR})
    return geometry.getExtent()
}

function deserialize(serialized) {
    if (serialized && serialized.length === 4) {
        return ol.proj.transformExtent(serialized, WGS84, WEB_MERCATOR)
    }
    return null
}

function serialize(extent) {
    const bbox = ol.proj.transformExtent(extent, WEB_MERCATOR, WGS84)
    const p1 = unwrapPoint(bbox.slice(0, 2))
    const p2 = unwrapPoint(bbox.slice(2, 4))
    return p1.concat(p2).map(truncate)
}

function isGeoJSONValid(geojson) {
    const parser = new jsts.io.GeoJSONReader();
    const jstsGeom = parser.read(geojson);
    const valid = jstsGeom.features[0].geometry.isValid();
    return valid;
}

function createGeoJSON(ol3Geometry) {
    const bbox = serialize(ol3Geometry.getExtent());
    const coords = ol3Geometry.getCoordinates();
    // need to apply transform to a cloned geom but simple geometry does not support .clone() operation.
    const polygonGeom = new ol.geom.Polygon(coords)
    polygonGeom.transform(WEB_MERCATOR, WGS84);
    const wgs84Coords = polygonGeom.getCoordinates();
    const geojson = {"type": "FeatureCollection",
                    "features": [
                        {
                            "type": "Feature",
                            "bbox": bbox,
                            "geometry": {"type": "Polygon", "coordinates": wgs84Coords}
                        }
                    ]}
    return geojson;
}

function processGeoJSONFile(file) {
    const reader = new FileReader();
    reader.onload = () => {
        const dataURL = reader.result;
        const geojsonReader = new ol.format.GeoJSON();
        const geom = geojsonReader.readFeatures(JSON.parse(dataURL));
        return geom;
    }
    return reader.readAsText(file);
}

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
