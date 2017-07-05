import PropTypes from 'prop-types';
import React, { Component } from 'react';
import { connect } from 'react-redux';
import Attribution from 'ol/control/attribution';
import Control from 'ol/control/control';
import Draw from 'ol/interaction/draw';
import Feature from 'ol/feature';
import Fill from 'ol/style/fill';
import GeoJSONFormat from 'ol/format/geojson';
import interaction from 'ol/interaction';
import Polygon from 'ol/geom/polygon';
import Projection from 'ol/proj/projection';
import Map from 'ol/map';
import ol from 'ol';
import OSM from 'ol/source/osm';
import proj from 'ol/proj';
import RegularShape from 'ol/style/regularshape';
import ScaleLine from 'ol/control/scaleline';
import Sphere from 'ol/sphere';
import Stroke from 'ol/style/stroke';
import Style from 'ol/style/style';
import Tile from 'ol/layer/tile';
import VectorLayer from 'ol/layer/vector';
import VectorSource from 'ol/source/vector';
import View from 'ol/view';
import Zoom from 'ol/control/zoom';

import styles from '../../styles/aoi/CreateExport.css';
import AoiInfobar from './AoiInfobar.js';
import SearchAOIToolbar from './SearchAOIToolbar.js';
import DrawAOIToolbar from './DrawAOIToolbar.js';
import InvalidDrawWarning from './InvalidDrawWarning.js';
import DropZone from './DropZone.js';
import {
  updateMode,
  updateAoiInfo,
  clearAoiInfo
} from '../../actions/exportsActions.js';
import {
  hideInvalidDrawWarning,
  showInvalidDrawWarning
} from '../../actions/aoi/drawToolBarActions.js';

export const MODE_DRAW_BBOX = 'MODE_DRAW_BBOX';
export const MODE_NORMAL = 'MODE_NORMAL';
export const MODE_DRAW_FREE = 'MODE_DRAW_FREE';
const WGS84 = 'EPSG:4326';
const WEB_MERCATOR = 'EPSG:3857';
const isEqual = require('lodash/isEqual');

const GEOJSON_FORMAT = new GeoJSONFormat();

export class ExportAOI extends Component {
  constructor (props) {
    super(props);
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
        return new Feature({
          geometry: GEOJSON_FORMAT.readGeometry(geojson, {
            dataProjection: WGS84,
            featureProjection: WEB_MERCATOR
          })
        });
    }
  }

  componentDidMount () {
    const { aoiInfo: { geojson } } = this.props;

    this._initializeOpenLayers();
    this._updateInteractions();

    if (geojson != null && Object.keys(geojson).length > 0) {
      const feature = this.getFeature(geojson);
      this._drawLayer.getSource().addFeature(feature);
      this.handleZoomToSelection(serialize(feature.getGeometry().getExtent()));
    }
  }

  checkSize (geometry) {
    var currentProjection = new Projection({ code: 'EPSG:3857' });
    var newProjection = new Projection({ code: 'EPSG:4326' });
    var extentPoly = Polygon.fromExtent(geometry.getExtent());
    extentPoly.transform(currentProjection, newProjection);
    var sphere = new Sphere(6378137);
    var areaSqkm = Math.round(
      Math.abs(
        sphere.geodesicArea(extentPoly.getCoordinates()[0]) / 1000 / 1000
      )
    );

    const MAX = 3000000;
    if (areaSqkm > MAX) {
      this.props.showInvalidDrawWarning(
        `The bounds of the polygon are too large: ${areaSqkm} sq km, max ${MAX}`
      );
    }
  }

  componentDidUpdate (prevProps, prevState) {
    if (this.props.errors) {
      this.props.showInvalidDrawWarning(this.props.errors);
    }
    if (!isEqual(prevProps.aoiInfo.geojson, this.props.aoiInfo.geojson)) {
      // remove existing features
      this._clearDraw();
      if (this.props.aoiInfo.geojson) {
        const feature = this.getFeature(this.props.aoiInfo.geojson);
        this._drawLayer.getSource().addFeature(feature);
        const geometry = feature.getGeometry();
        this.checkSize(geometry);
        this.handleZoomToSelection(serialize(geometry.getExtent()));

        if (this.props.aoiInfo.geojson.features) {
          this.props.setFormGeoJSON(
            this.props.aoiInfo.geojson.features[0].geometry
          );
        } else if (this.props.aoiInfo.geojson.geometry) {
          this.props.setFormGeoJSON(this.props.aoiInfo.geojson.geometry);
        } else {
          this.props.setFormGeoJSON(this.props.aoiInfo.geojson);
        }
      } else {
        this.props.setFormGeoJSON(undefined);
      }
    }
  }

  componentWillReceiveProps (nextProps) {
    // Check if the map mode has changed (DRAW or NORMAL)
    if (this.props.mode !== nextProps.mode) {
      this._updateInteractions(nextProps.mode);
    }

    if (this.props.zoomToSelection.click !== nextProps.zoomToSelection.click) {
      this.handleZoomToSelection(nextProps.aoiInfo.geojson.features[0].bbox);
    }

    // Check if the reset map button has been clicked
    if (this.props.resetMap.click !== nextProps.resetMap.click) {
      this.handleResetMap();
    }

    if (nextProps.importGeom.processed && !this.props.importGeom.processed) {
      this.handleGeoJSONUpload(nextProps.importGeom.geojson);
    }
  }

  handleCancel (sender) {
    this.props.hideInvalidDrawWarning();

    if (this.props.mode !== MODE_NORMAL) {
      this.props.updateMode(MODE_NORMAL);
    }

    this._clearDraw();
    this.props.clearAoiInfo();
  }

  handleZoomToSelection (bbox) {
    this._map
      .getView()
      .fit(
        proj.transformExtent(bbox, WGS84, WEB_MERCATOR),
        this._map.getSize()
      );
  }

  handleResetMap () {
    let worldExtent = proj.transformExtent(
      [-180, -90, 180, 90],
      WGS84,
      WEB_MERCATOR
    );
    this._map.getView().fit(worldExtent, this._map.getSize());
  }

  handleSearch (result) {
    const unformattedBbox = result.bbox;
    const formattedBbox = [
      unformattedBbox.west,
      unformattedBbox.south,
      unformattedBbox.east,
      unformattedBbox.north
    ];
    this._clearDraw();
    this.props.hideInvalidDrawWarning();
    const bbox = formattedBbox.map(truncate);
    const mercBbox = proj.transformExtent(bbox, WGS84, WEB_MERCATOR);
    const geom = Polygon.fromExtent(mercBbox);
    const geojson = createGeoJSON(geom);
    const bboxFeature = new Feature({
      geometry: geom
    });
    this._drawLayer.getSource().addFeature(bboxFeature);
    let description = '';
    description = description + (result.countryName ? result.countryName : '');
    description =
      description + (result.adminName1 ? ', ' + result.adminName1 : '');
    description =
      description + (result.adminName2 ? ', ' + result.adminName2 : '');

    this.props.updateAoiInfo(geojson, 'Polygon', result.name, description);
    this.handleZoomToSelection(bbox);
  }

  handleGeoJSONUpload (geojson) {
    this.props.updateAoiInfo(geojson, 'Polygon', 'Custom Polygon', 'Import');
  }

  setMapView () {
    this._clearDraw();
    const extent = this._map.getView().calculateExtent(this._map.getSize());
    const geom = Polygon.fromExtent(extent);
    const geojson = createGeoJSON(geom);
    this.props.updateAoiInfo(geojson, 'Polygon', 'Custom Polygon', 'Map View');
  }

  _activateDrawInteraction (mode) {
    if (mode === MODE_DRAW_BBOX) {
      this._drawFreeInteraction.setActive(false);
      this._drawBoxInteraction.setActive(true);
    } else if (mode === MODE_DRAW_FREE) {
      this._drawBoxInteraction.setActive(false);
      this._drawFreeInteraction.setActive(true);
    }
  }

  _clearDraw () {
    this._drawLayer.getSource().clear();
  }

  _deactivateDrawInteraction () {
    this._drawBoxInteraction.setActive(false);
    this._drawFreeInteraction.setActive(false);
  }

  _handleDrawEnd (event) {
    // get the drawn bounding box
    const geometry = event.feature.getGeometry();
    const geojson = createGeoJSON(geometry);
    this.props.updateAoiInfo(geojson, 'Polygon', 'Custom Polygon', 'Draw');
    this.props.updateMode('MODE_NORMAL');
  }

  _handleDrawStart () {
    this._clearDraw();
  }

  _initializeOpenLayers () {
    this._drawLayer = generateDrawLayer();
    this._drawBoxInteraction = _generateDrawBoxInteraction(this._drawLayer);
    this._drawBoxInteraction.on('drawstart', this._handleDrawStart);
    this._drawBoxInteraction.on('drawend', this._handleDrawEnd);

    this._drawFreeInteraction = _generateDrawFreeInteraction(this._drawLayer);
    this._drawFreeInteraction.on('drawstart', this._handleDrawStart);
    this._drawFreeInteraction.on('drawend', this._handleDrawEnd);

    this._map = new Map({
      controls: [
        new ScaleLine({
          className: styles.olScaleLine
        }),
        new Attribution({
          collapsible: false,
          collapsed: false
        }),
        new Zoom({
          className: styles.olZoom
        }),
        new ZoomExtent({
          className: styles.olZoomToExtent,
          extent: [
            -14251567.50789682,
            -10584983.780136958,
            14251787.50789682,
            10584983.780136958
          ]
        })
      ],
      interactions: interaction.defaults({
        keyboard: false,
        altShiftDragRotate: false,
        pinchRotate: false
      }),
      layers: [
        // Order matters here
        new Tile({
          source: new OSM()
        })
      ],
      target: 'map',
      view: new View({
        projection: 'EPSG:3857',
        center: [110, 0],
        zoom: 3,
        minZoom: 3,
        maxZoom: 22
      })
    });

    this._map.addInteraction(this._drawBoxInteraction);
    this._map.addInteraction(this._drawFreeInteraction);
    this._map.addLayer(this._drawLayer);
  }

  render () {
    const mapStyle = {};

    return (
      <div>
        <div id='map' className={styles.map} style={mapStyle} ref='olmap'>
          <AoiInfobar />
          <SearchAOIToolbar
            handleSearch={result => this.handleSearch(result)}
            handleCancel={sender => this.handleCancel(sender)}
          />
          <DrawAOIToolbar
            handleCancel={sender => this.handleCancel(sender)}
            setMapView={this.setMapView}
          />
          <InvalidDrawWarning />
          <DropZone />
        </div>
      </div>
    );
  }

  _updateInteractions (mode) {
    switch (mode) {
      case MODE_DRAW_BBOX:
        this._activateDrawInteraction(MODE_DRAW_BBOX);
        break;
      case MODE_DRAW_FREE:
        this._activateDrawInteraction(MODE_DRAW_FREE);
        break;
      case MODE_NORMAL:
        this._deactivateDrawInteraction();
        break;
    }
  }
}

ExportAOI.propTypes = {
  aoiInfo: PropTypes.object,
  errors: PropTypes.array,
  mode: PropTypes.string,
  zoomToSelection: PropTypes.object,
  resetMap: PropTypes.object,
  importGeom: PropTypes.object,
  updateMode: PropTypes.func,
  hideInvalidDrawWarning: PropTypes.func,
  showInvalidDrawWarning: PropTypes.func,
  updateAoiInfo: PropTypes.func,
  clearAoiInfo: PropTypes.func,
  setFormGeoJSON: PropTypes.func
};

function mapStateToProps (state) {
  return {
    aoiInfo: state.aoiInfo,
    mode: state.mode,
    zoomToSelection: state.zoomToSelection,
    resetMap: state.resetMap,
    importGeom: state.importGeom
  };
}

function mapDispatchToProps (dispatch) {
  return {
    updateMode: newMode => {
      dispatch(updateMode(newMode));
    },
    hideInvalidDrawWarning: () => {
      dispatch(hideInvalidDrawWarning());
    },
    showInvalidDrawWarning: msg => {
      dispatch(showInvalidDrawWarning(msg));
    },
    updateAoiInfo: (geojson, geomType, title, description) => {
      dispatch(updateAoiInfo(geojson, geomType, title, description));
    },
    clearAoiInfo: () => {
      dispatch(clearAoiInfo());
    }
  };
}

export default connect(mapStateToProps, mapDispatchToProps)(ExportAOI);

function generateDrawLayer () {
  return new VectorLayer({
    source: new VectorSource({
      wrapX: false
    }),
    style: new Style({
      fill: new Fill({
        color: 'hsla(202, 70%, 50%, .35)'
      }),
      stroke: new Stroke({
        color: 'hsla(202, 70%, 50%, .7)',
        width: 1,
        lineDash: [5, 5]
      })
    })
  });
}

function _generateDrawBoxInteraction (drawLayer) {
  const draw = new Draw({
    source: drawLayer.getSource(),
    maxPoints: 2,
    type: 'LineString',
    geometryFunction (coordinates, geometry) {
      geometry = geometry || new Polygon(null);
      const [[x1, y1], [x2, y2]] = coordinates;
      geometry.setCoordinates([
        [[x1, y1], [x1, y2], [x2, y2], [x2, y1], [x1, y1]]
      ]);
      return geometry;
    },
    style: new Style({
      image: new RegularShape({
        stroke: new Stroke({
          color: 'black',
          width: 1
        }),
        points: 4,
        radius: 15,
        radius2: 0,
        angle: 0
      }),
      fill: new Fill({
        color: 'hsla(202, 70%, 50%, .6)'
      }),
      stroke: new Stroke({
        color: 'hsl(202, 70%, 50%)',
        width: 1,
        lineDash: [5, 5]
      })
    })
  });
  draw.setActive(false);
  return draw;
}

function _generateDrawFreeInteraction (drawLayer) {
  const draw = new Draw({
    source: drawLayer.getSource(),
    type: 'Polygon',
    freehand: false,
    style: new Style({
      image: new RegularShape({
        stroke: new Stroke({
          color: 'black',
          width: 1
        }),
        points: 4,
        radius: 15,
        radius2: 0,
        angle: 0
      }),
      fill: new Fill({
        color: 'hsla(202, 70%, 50%, .6)'
      }),
      stroke: new Stroke({
        color: 'hsl(202, 70%, 50%)',
        width: 1,
        lineDash: [5, 5]
      })
    })
  });
  draw.setActive(false);
  return draw;
}

function truncate (number) {
  return Math.round(number * 100) / 100;
}

function unwrapPoint ([x, y]) {
  return [x > 0 ? Math.min(180, x) : Math.max(-180, x), y];
}

function serialize (extent) {
  const bbox = proj.transformExtent(extent, WEB_MERCATOR, WGS84);
  const p1 = unwrapPoint(bbox.slice(0, 2));
  const p2 = unwrapPoint(bbox.slice(2, 4));
  return p1.concat(p2).map(truncate);
}

function createGeoJSON (ol3Geometry) {
  const bbox = serialize(ol3Geometry.getExtent());
  const coords = ol3Geometry.getCoordinates();
  // need to apply transform to a cloned geom but simple geometry does not support .clone() operation.
  const polygonGeom = new Polygon(coords);
  polygonGeom.transform(WEB_MERCATOR, WGS84);
  const wgs84Coords = polygonGeom.getCoordinates();
  const geojson = {
    type: 'FeatureCollection',
    features: [
      {
        type: 'Feature',
        bbox: bbox,
        geometry: { type: 'Polygon', coordinates: wgs84Coords }
      }
    ]
  };
  return geojson;
}

const ZoomExtent = function (options) {
  options = options || {};
  options.className = options.className != null ? options.className : '';

  let button = document.createElement('button');
  let icon = document.createElement('i');
  icon.className = 'fa fa-globe';
  button.appendChild(icon);
  let this_ = this;

  this.zoomer = () => {
    const map = this_.getMap();
    const view = map.getView();
    const size = map.getSize();
    view.fit(options.extent, size);
  };

  button.addEventListener('click', this_.zoomer, false);
  button.addEventListener('touchstart', this_.zoomer, false);
  let element = document.createElement('div');
  element.className = options.className + ' ol-unselectable ol-control';
  element.appendChild(button);

  Control.call(this, {
    element: element,
    target: options.target
  });
};
ol.inherits(ZoomExtent, Control);
