import { RangeSlider } from "@blueprintjs/core";
import React, { Component } from "react";
import { Alert, Col, Row } from "react-bootstrap";
import { Creatable } from "react-select";

const TILE_SOURCES = [
  {
    label: "OpenStreetMap",
    value: "http://tile.openstreetmap.org/{z}/{x}/{y}.png"
  }
];

export default class TileSourceField extends Component {
  render() {
    const {
      mbtiles_source: { meta: { error } },
      mbtiles_maxzoom: { input: maxZoomInput },
      mbtiles_minzoom: { input: minZoomInput },
      mbtiles_source: { input: sourceInput }
    } = this.props;

    return (
      <div>
        <Row>
          <h3 style={{ marginTop: 15 }}>MBTiles Source</h3>
        </Row>
        {error &&
          <Row>
            <Alert bsStyle="danger">
              {error}
            </Alert>
          </Row>}
        <Row>
          <Col md={5}>
            <label>Source:</label>
            <Creatable
              isValidNewOption={({ label }) =>
                (label || "").match(/^https?:\/\//)}
              options={TILE_SOURCES}
              onChange={val => sourceInput.onChange(val ? val.value : null)}
              value={sourceInput.value || null}
            />
          </Col>
          <Col md={5} mdOffset={1}>
            <label>Zoom Range:</label>{" "}
            <RangeSlider
              labelStepSize={5}
              max={18}
              onChange={([min, max]) => {
                minZoomInput.onChange(min);
                maxZoomInput.onChange(max);
              }}
              value={[minZoomInput.value, maxZoomInput.value]}
            />
          </Col>
        </Row>
      </div>
    );
  }
}
