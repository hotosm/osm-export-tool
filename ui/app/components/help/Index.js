import React from "react";
import { Link } from "react-router-dom";
import { Jumbotron, Button, Panel, Row, Col } from 'react-bootstrap';

export default () =>
  <div className="help">
    <Jumbotron className="hero">
      <h1>Welcome</h1>
      <p>The Export Tool creates up-to-date OSM extracts in various file formats. Learn more about the Export Tool below.</p>
    </Jumbotron>
    <section className="helpItems">
      <div className="helpItemsBody">
        <Row>
          <Col sm={4} className="itemWrapper">
            <Panel>
              <h2>Quick Start</h2>
              <p>First time using the Export Tool? Use this guide to get started.</p>
              <Button href="help/quick_start">View</Button>
            </Panel>
          </Col>
          <Col sm={4} className="itemWrapper">
            <Panel>
              <h2>Browsing Exports</h2>
              <p>Learn to browse, run and clone exports already created by other users and humanitarian organizations.</p>
              <Button href="help/browsing_exports">View</Button>
            </Panel>
          </Col>
          <Col sm={4} className="itemWrapper">
            <Panel>
              <h2>Selecting Features</h2>
              <p>How to specify what features are selected by the Export Tool.</p>
              <ul>
                <li>Tag Tree</li>
                <li>Storing Configurations</li>
              </ul>
              <Button href="help/feature_selections">View</Button>
            </Panel>
          </Col>
        </Row>
        <Row>
          <Col sm={4} className="itemWrapper">
            <Panel>
              <h2>YAML Specification</h2>
              <p>Detailed information on the YAML feature selection format.</p>
              <Button href="help/yaml">View</Button>
            </Panel>
          </Col>
          <Col sm={4} className="itemWrapper">
            <Panel>
              <h2>File Formats</h2>
              <p>Details on file formats available for export from the Export Tool.</p>
              <ul>
                <li>
                  <Link to="help/export_formats#shp">Esri Shapefile (.SHP)</Link>
                </li>
                <li>
                  <Link to="help/export_formats#img">Garmin .IMG</Link>
                </li>
                <li>
                  <Link to="help/export_formats#kmz">Google Earth KML (.KMZ)</Link>
                </li>
                <li>
                  <Link to="help/export_formats#pbf">OpenStreetMap Protobuf (.PBF)</Link>
                </li>
                <li>
                  <Link to="help/export_formats#gpkg">OGC Geopackage (.GPKG)</Link>
                </li>
              </ul>
              <Button href="help/browsing_exports">View</Button>
            </Panel>
          </Col>
          <Col sm={4} className="itemWrapper">
            <Panel>
              <h2>Export Tool API</h2>
              <p>Creating Exports programatically via the JSON API.</p>
              <Button href="help/api">View</Button>
            </Panel>
          </Col>

        </Row>
      </div>
    </section>
  </div>;
