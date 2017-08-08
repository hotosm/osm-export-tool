import React from "react";
import { Button, ButtonGroup } from "react-bootstrap";
import ReactDOM from "react-dom";
import Control from "ol/control/control";
import Draw from "ol/interaction/draw";
import Fill from "ol/style/fill";
import Polygon from "ol/geom/polygon";
import RegularShape from "ol/style/regularshape";
import Stroke from "ol/style/stroke";
import Style from "ol/style/style";
import VectorLayer from "ol/layer/vector";
import VectorSource from "ol/source/vector";
import detectIt from "detect-it";
import ol from "ol";
import proj from "ol/proj";

const WGS84 = "EPSG:4326";
const WEB_MERCATOR = "EPSG:3857";

function generateDrawLayer() {
  return new VectorLayer({
    source: new VectorSource({
      wrapX: false
    }),
    style: new Style({
      fill: new Fill({
        color: "rgba(235, 80, 85, .6)"
      }),
      stroke: new Stroke({
        color: "rgba(235, 80, 85, .7)",
        width: 1,
        lineDash: [5, 5]
      })
    })
  });
}

const FilterControl = function({ onUpdate, render, target }) {
  onUpdate = onUpdate || (() => null);

  const drawLayer = generateDrawLayer();
  const source = drawLayer.getSource();

  const draw = new Draw({
    source,
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
        color: "rgba(235, 80, 85, .6)"
      }),
      stroke: new Stroke({
        color: "rgba(235, 80, 85, .7)",
        width: 1,
        lineDash: [5, 5]
      })
    })
  });

  draw.setActive(false);

  draw.on("drawstart", () => source.clear());
  draw.on("drawend", ({ feature }) => {
    draw.setActive(false);

    onUpdate(
      proj.transformExtent(
        feature.getGeometry().getExtent(),
        WEB_MERCATOR,
        WGS84
      )
    );
  });

  let added = false;

  const startDrawing = () => {
    if (!added) {
      this.getMap().addLayer(drawLayer);
      this.getMap().addInteraction(draw);

      added = true;
    }

    draw.setActive(true);
  };

  const clearFilter = () => {
    source.clear();

    onUpdate([]);
  };

  const element = document.createElement("div");
  let filter;
  let clear;

  ReactDOM.render(
    <div className="ol-filter">
      <ButtonGroup>
        <Button bsStyle="primary" ref={f => (filter = f)} type="button">
          Filter Area
        </Button>
        <Button
          bsStyle="primary"
          onClick={() => console.log("click")}
          ref={c => (clear = c)}
          type="button"
        >
          Clear Filter
        </Button>
      </ButtonGroup>
    </div>,
    element
  );

  clear = ReactDOM.findDOMNode(clear);
  filter = ReactDOM.findDOMNode(filter);

  clear.addEventListener("click", clearFilter, false);
  clear.addEventListener(
    "touchstart",
    clearFilter,
    detectIt.passiveEvents ? { passive: true } : false
  );
  filter.addEventListener("click", startDrawing, false);
  filter.addEventListener(
    "touchstart",
    startDrawing,
    detectIt.passiveEvents ? { passive: true } : false
  );

  Control.call(this, {
    element,
    target
  });
};

ol.inherits(FilterControl, Control);

export default FilterControl;
