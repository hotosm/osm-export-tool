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
  componentDidMount() {
    const {
      mbtiles_maxzoom: { input: maxZoomInput },
      mbtiles_minzoom: { input: minZoomInput },
    } = this.props;

    if (maxZoomInput.value == null || maxZoomInput.value === "") {
      maxZoomInput.onChange(10);
    }

    if (minZoomInput == null || minZoomInput.value === "") {
      minZoomInput.onChange(0);
    }
  }

  render() {
    const {
      mbtiles_source: { meta: { error } },
      mbtiles_maxzoom: { input: maxZoomInput },
      mbtiles_minzoom: { input: minZoomInput },
      mbtiles_source: { input: sourceInput }
    } = this.props;

    let options = TILE_SOURCES;

    if (
      sourceInput.value &&
      !TILE_SOURCES.some(({ value }) => value === sourceInput.value)
    ) {
      options = options.concat({
        label: sourceInput.value,
        value: sourceInput.value
      });
    }

    return (
      <div>
        <Row>
          <h3 style={{ marginTop: 15 }}>Tiles Source</h3>
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
              options={options}
              onChange={val => sourceInput.onChange(val ? val.value : null)}
              value={sourceInput.value || null}
            />
          </Col>
          <Col md={5} mdOffset={1}>
            <label>Zoom Range:</label>{" "}
            <RangeSlider
              labelStepSize={5}
              max={20}
              onChange={([min, max]) => {
                minZoomInput.onChange(min);
                maxZoomInput.onChange(max);
              }}
              value={[minZoomInput.value || 0, maxZoomInput.value || 10]}
            />
          </Col>
        </Row>
      </div>
    );
  }
}
