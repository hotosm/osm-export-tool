import bbox from "@turf/bbox";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { connect } from "react-redux";
import Attribution from "ol/control/attribution";
import Draw from "ol/interaction/draw";
import Feature from "ol/feature";
import { feature, featureCollection, polygon } from "@turf/helpers";
import Fill from "ol/style/fill";
import GeoJSONFormat from "ol/format/geojson";
import interaction from "ol/interaction";
import LayerAttribution from "ol/attribution";
import Map from "ol/map";
import OSM from "ol/source/osm";
import Polygon from "ol/geom/polygon";
import proj from "ol/proj";
import RegularShape from "ol/style/regularshape";
import ScaleLine from "ol/control/scaleline";
import Stroke from "ol/style/stroke";
import Style from "ol/style/style";
import Tile from "ol/layer/tile";
import VectorLayer from "ol/layer/vector";
import VectorSource from "ol/source/vector";
import View from "ol/view";
import Zoom from "ol/control/zoom";

import styles from "../../styles/aoi/CreateExport.css";
import AoiInfobar from "./AoiInfobar.js";
import SearchAOIToolbar from "./SearchAOIToolbar.js";
import DrawAOIToolbar from "./DrawAOIToolbar.js";
import InvalidDrawWarning from "./InvalidDrawWarning.js";
import DropZone from "./DropZone.js";
import ZoomExtent from "../ZoomExtent";
import { updateMode } from "../../actions/exports";

export const MODE_DRAW_BBOX = "MODE_DRAW_BBOX";
export const MODE_NORMAL = "MODE_NORMAL";
export const MODE_DRAW_FREE = "MODE_DRAW_FREE";
const WGS84 = "EPSG:4326";
const WEB_MERCATOR = "EPSG:3857";
const isEqual = require("lodash/isEqual");

const GEOJSON_FORMAT = new GeoJSONFormat();

export class ExportAOI extends Component {
  static propTypes = {
    aoi: PropTypes.shape({
      description: PropTypes.string,
      geojson: PropTypes.object,
      geomType: PropTypes.string,
      title: PropTypes.string
    }),
    errors: PropTypes.any,
    mode: PropTypes.string,
    importGeom: PropTypes.object,
    updateMode: PropTypes.func,
    updateAoiInfo: PropTypes.func,
    clearAoiInfo: PropTypes.func,
  };

  getFeature(geojson) {
    switch (geojson.type) {
      case "FeatureCollection":
        return GEOJSON_FORMAT.readFeature(geojson.features[0], {
          dataProjection: WGS84,
          featureProjection: WEB_MERCATOR
        });

      case "Feature":
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

  componentDidMount() {
    const { aoi: { geojson } } = this.props;

    this._initializeOpenLayers();
    this._updateInteractions();

    if (geojson != null && Object.keys(geojson).length > 0) {
      const feature = this.getFeature(geojson);
      this._drawLayer.getSource().addFeature(feature);
      this.handleZoomToSelection(serialize(feature.getGeometry().getExtent()));
    }
  }

  componentDidUpdate(prevProps, prevState) {
    if (!isEqual(prevProps.aoi.geojson, this.props.aoi.geojson)) {
      // remove existing features
      this._clearDraw();
      if (this.props.aoi.geojson) {
        const feature = this.getFeature(this.props.aoi.geojson);
        this._drawLayer.getSource().addFeature(feature);
        this.handleZoomToSelection(bbox(this.props.aoi.geojson));
      }
    }
  }

  componentWillReceiveProps(nextProps) {
    // Check if the map mode has changed (DRAW or NORMAL)
    if (this.props.mode !== nextProps.mode) {
      this._updateInteractions(nextProps.mode);
    }

    if (nextProps.importGeom.processed && !this.props.importGeom.processed) {
      this.handleGeoJSONUpload(nextProps.importGeom.geojson);
    }
  }

  handleCancel = sender => {
    if (this.props.mode !== MODE_NORMAL) {
      this.props.updateMode(MODE_NORMAL);
    }

    this._clearDraw();
    this.props.clearAoiInfo();
  };

  handleZoomToSelection = bbox =>
    this._map
      .getView()
      .fit(
        proj.transformExtent(bbox, WGS84, WEB_MERCATOR),
        this._map.getSize()
      );

  handleSearch = result => {
    var geojson;
    if (result.adminName2 && result.adminName2.startsWith('ISO3')){
      try {
        geojson = JSON.parse(JSON.stringify(result.bbox));
      } catch (e) {
        alert(e);
      }
      // extract single feature geometry from collection
      if (geojson.type === "FeatureCollection") {
              if (geojson.features.length === 1) {
                geojson = geojson.features[0].geometry;
              }
            }
      if (["Polygon", "MultiPolygon"].includes(geojson.type)) {
              geojson = featureCollection([feature(geojson)]);
            }

    }
    else if (result.adminName2 == 'TM' || result.adminName2 == 'OSM') {
      this._clearDraw();
      geojson = result.bbox;
    }
    else {
      const unformattedBbox = result.bbox;
      const formattedBbox = [
        unformattedBbox.west,
        unformattedBbox.south,
        unformattedBbox.east,
        unformattedBbox.north
      ];
      this._clearDraw();
      const bbox = formattedBbox.map(truncate);
      const mercBbox = proj.transformExtent(bbox, WGS84, WEB_MERCATOR);
      const geom = Polygon.fromExtent(mercBbox);
      geojson = createGeoJSON(geom);
      const bboxFeature = new Feature({
        geometry: geom
      });

    }
    //this._drawLayer.getSource().addFeature(bboxFeature);
    let description = "";
    description += result.countryName ? result.countryName : "";
    description += result.adminName1 ? ", " + result.adminName1 : "";
    description += result.adminName2 ? ", " + result.adminName2 : "";

    this.props.updateAoiInfo(geojson, "Polygon", result.name, description);
    this.handleZoomToSelection(bbox);
  };

  handleSearchNominatim = result => {
    this.props.updateAoiInfo(result.geojson, "Polygon", result.name, result.description);
  }

  handleGeoJSONUpload = geojson =>
    this.props.updateAoiInfo(geojson, "Polygon", "Custom Polygon", "Import");

  setMapView = () => {
    this._clearDraw();
    const extent = this._map.getView().calculateExtent(this._map.getSize());
    const geom = Polygon.fromExtent(extent);
    const geojson = createGeoJSON(geom);
    this.props.updateAoiInfo(geojson, "Polygon", "Custom Polygon", "Map View");
  };

  _activateDrawInteraction(mode) {
    if (mode === MODE_DRAW_BBOX) {
      this._drawFreeInteraction.setActive(false);
      this._drawBoxInteraction.setActive(true);
    } else if (mode === MODE_DRAW_FREE) {
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

  _handleDrawEnd = event => {
    // get the drawn bounding box
    const geometry = event.feature.getGeometry();
    const geojson = createGeoJSON(geometry);
    this.props.updateAoiInfo(geojson, "Polygon", "Custom Polygon", "Draw");
    this.props.updateMode("MODE_NORMAL");
  };

  _handleDrawStart = () => this._clearDraw();

  _initializeOpenLayers() {
    this._drawLayer = generateDrawLayer();
    this._drawBoxInteraction = _generateDrawBoxInteraction(this._drawLayer);
    this._drawBoxInteraction.on("drawstart", this._handleDrawStart);
    this._drawBoxInteraction.on("drawend", this._handleDrawEnd);

    this._drawFreeInteraction = _generateDrawFreeInteraction(this._drawLayer);
    this._drawFreeInteraction.on("drawstart", this._handleDrawStart);
    this._drawFreeInteraction.on("drawend", this._handleDrawEnd);

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
          source: new OSM({
            attributions: [
              new LayerAttribution({
                html: `© <a href="https://osm.org/">OSM</a>`
              }),
              OSM.ATTRIBUTION
            ],
            url:
              "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
          })
        })
      ],
      target: "map",
      view: new View({
        projection: "EPSG:3857",
        center: [110, 0],
        zoom: 2,
        minZoom: 2,
        maxZoom: 22
      })
    });

    this._map.addInteraction(this._drawBoxInteraction);
    this._map.addInteraction(this._drawFreeInteraction);
    this._map.addLayer(this._drawLayer);
  }

  zoomToSelection = () => {
    const { aoi: { geojson } } = this.props;

    this.handleZoomToSelection(bbox(geojson));
  };

  render() {
    const { aoi, aoi: { geojson }, errors } = this.props;

    return (
      <div>
        <div id="map" className={styles.map} ref="olmap">
          {geojson &&
            <AoiInfobar aoi={aoi} zoomToSelection={this.zoomToSelection} />}
          <SearchAOIToolbar
            handleSearch={this.handleSearch}
            handleSearchNominatim={this.handleSearchNominatim}
            handleCancel={this.handleCancel}
          />
          <DrawAOIToolbar
            handleCancel={this.handleCancel}
            setMapView={this.setMapView}
          />
          <InvalidDrawWarning msg={errors} />
          <DropZone />
        </div>
      </div>
    );
  }

  _updateInteractions(mode) {
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

      default:
        console.warn("Unrecognized interaction mode:", mode);
    }
  }
}

function mapStateToProps(state) {
  return {
    mode: state.mode,
    zoomToSelection: state.zoomToSelection,
    importGeom: state.importGeom
  };
}

export default connect(mapStateToProps, {
  updateMode,
})(ExportAOI);

function generateDrawLayer() {
  return new VectorLayer({
    source: new VectorSource({
      wrapX: false
    }),
    style: new Style({
      fill: new Fill({
        color: "hsla(202, 70%, 50%, .35)"
      }),
      stroke: new Stroke({
        color: "hsla(202, 70%, 50%, .7)",
        width: 1,
        lineDash: [5, 5]
      })
    })
  });
}

function _generateDrawBoxInteraction(drawLayer) {
  const draw = new Draw({
    source: drawLayer.getSource(),
    maxPoints: 2,
    type: "LineString",
    geometryFunction(coordinates, geometry) {
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
          color: "black",
          width: 1
        }),
        points: 4,
        radius: 15,
        radius2: 0,
        angle: 0
      }),
      fill: new Fill({
        color: "hsla(202, 70%, 50%, .6)"
      }),
      stroke: new Stroke({
        color: "hsl(202, 70%, 50%)",
        width: 1,
        lineDash: [5, 5]
      })
    })
  });
  draw.setActive(false);
  return draw;
}

function _generateDrawFreeInteraction(drawLayer) {
  const draw = new Draw({
    source: drawLayer.getSource(),
    type: "Polygon",
    freehand: false,
    style: new Style({
      image: new RegularShape({
        stroke: new Stroke({
          color: "black",
          width: 1
        }),
        points: 4,
        radius: 15,
        radius2: 0,
        angle: 0
      }),
      fill: new Fill({
        color: "hsla(202, 70%, 50%, .6)"
      }),
      stroke: new Stroke({
        color: "hsl(202, 70%, 50%)",
        width: 1,
        lineDash: [5, 5]
      })
    })
  });
  draw.setActive(false);
  return draw;
}

function truncate(number) {
  return Math.round(number * 100) / 100;
}

function unwrapPoint([x, y]) {
  return [x > 0 ? Math.min(180, x) : Math.max(-180, x), y];
}

function serialize(extent) {
  const bbox = proj.transformExtent(extent, WEB_MERCATOR, WGS84);
  const p1 = unwrapPoint(bbox.slice(0, 2));
  const p2 = unwrapPoint(bbox.slice(2, 4));
  return p1.concat(p2).map(truncate);
}

function createGeoJSON(ol3Geometry) {
  const bbox = serialize(ol3Geometry.getExtent());
  const coords = ol3Geometry.getCoordinates();
  // need to apply transform to a cloned geom but simple geometry does not support .clone() operation.
  const polygonGeom = new Polygon(coords);
  polygonGeom.transform(WEB_MERCATOR, WGS84);
  const wgs84Coords = polygonGeom.getCoordinates();
  const geojson = {
    type: "FeatureCollection",
    features: [
      {
        type: "Feature",
        bbox: bbox,
        geometry: { type: "Polygon", coordinates: wgs84Coords }
      }
    ]
  };
  return geojson;
}
