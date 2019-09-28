import React from "react";
import { Link } from "react-router-dom";
import { Row, Col } from "react-bootstrap";
import MapListView from "./MapListView";

export default () =>
  <Row style={{ height: "100%" }}>
    <Col xs={6} style={{ height: "100%", padding: "20px" }}>
      <h1>Stats</h1>
      Exports
      Past day
      Past week
      Past month


      Users
      Past day
      Past week
      Past month

      File formats in past month
    </Col>
    <Col xs={6} style={{ height: "100%" }}>
      <MapListView features={{features:[],"type":"FeatureCollection"}} />
    </Col>
  </Row>;

