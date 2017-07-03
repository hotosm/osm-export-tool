import React, { Component, PropTypes } from 'react';
import isEqual from 'lodash/isEqual';
import Attribution from 'ol/control/attribution';
import Control from 'ol/control/control';
import Fill from 'ol/style/fill';
import GeoJSONFormat from 'ol/format/geojson';
import interaction from 'ol/interaction';
import Map from 'ol/map';
import ol from 'ol';
import OSM from 'ol/source/osm';
import proj from 'ol/proj';
import ScaleLine from 'ol/control/scaleline';
import Stroke from 'ol/style/stroke';
import Style from 'ol/style/style';
import Tile from 'ol/layer/tile';
import VectorLayer from 'ol/layer/vector';
import VectorSource from 'ol/source/vector';
import View from 'ol/view';
import Zoom from 'ol/control/zoom';

import styles from '../styles/aoi/CreateExport.css';

const jsts = require('jsts');

const GEOJSON_FORMAT = new GeoJSONFormat();
const GEOJSON_READER = new jsts.io.GeoJSONReader();
const WGS84 = 'EPSG:4326';
const WEB_MERCATOR = 'EPSG:3857';

export default class MapListView extends Component {
  static propTypes = {
    features: PropTypes.shape({
      features: PropTypes.array,
      geomType: PropTypes.string,
      type: PropTypes.string
    }),
    selectedFeatureId: PropTypes.number
  };

  state = {
    _features: []
  };

  componentDidMount () {
    this._initializeOpenLayers();

    if (this.props.features) {
      this.updateFeatures(this.props.features);
    }
    if (this.props.selectedFeatureId) {
      this.zoomToFeatureId(this.props.selectedFeatureId);
    }
  }

  componentDidUpdate (prevProps, prevState) {
    const { features, selectedFeatureId } = this.props;

    if (!isEqual(prevProps.features, features)) {
      this.updateFeatures(features);
    }

    if (prevProps.selectedFeatureId !== selectedFeatureId) {
      this.zoomToFeatureId(selectedFeatureId);
    }
  }

  handleResetMap () {
    const worldExtent = proj.transformExtent(
      [-180, -90, 180, 90],
      WGS84,
      WEB_MERCATOR
    );
    this._map.getView().fit(worldExtent, this._map.getSize());
  }

  updateFeatures (features) {
    this._clearDraw();

    GEOJSON_FORMAT.readFeatures(features, {
      dataProjection: WGS84,
      featureProjection: WEB_MERCATOR
    }).forEach(feature => {
      this._drawLayer.getSource().addFeature(feature);
    });
  }

  zoomToFeatureId (id) {
    const { features } = this.props;

    const selectedFeature = features.features.filter(x => x.id === id).shift();

    if (selectedFeature != null) {
      const envelope = GEOJSON_READER.read(selectedFeature)
        .getEnvelope()
        .getCoordinates();

      const bbox = [envelope[0], envelope[2]]
        .map(c => [c.x, c.y])
        .reduce((acc, val) => acc.concat(val), []);

      this._map
        .getView()
        .fit(
          proj.transformExtent(bbox, WGS84, WEB_MERCATOR),
          this._map.getSize()
        );
    }
  }

  _clearDraw () {
    this._drawLayer.getSource().clear();
  }

  _generateDrawLayer () {
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

  _initializeOpenLayers () {
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
        projection: WEB_MERCATOR,
        center: [110, 0],
        zoom: 3,
        minZoom: 3,
        maxZoom: 22
      })
    });

    this._drawLayer = this._generateDrawLayer();
    this._map.addLayer(this._drawLayer);
  }

  render () {
    return (
      <div>
        <div id='map' className={styles.map} ref='olmap' />
      </div>
    );
  }
}

const ZoomExtent = function (options = {}) {
  options.className = options.className || '';

  const button = document.createElement('button');
  const icon = document.createElement('i');
  icon.className = 'fa fa-globe';
  button.appendChild(icon);

  this.zoomer = () => {
    const map = this.getMap();
    const view = map.getView();
    const extent = options.extent || view.getProjection.getExtent();
    const size = map.getSize();

    view.fit(extent, size);
  };

  button.addEventListener('click', this.zoomer, false);
  button.addEventListener('touchstart', this.zoomer, false);

  const element = document.createElement('div');
  element.className = options.className + ' ol-unselectable ol-control';
  element.appendChild(button);

  Control.call(this, {
    element: element,
    target: options.target
  });
};

ol.inherits(ZoomExtent, Control);
