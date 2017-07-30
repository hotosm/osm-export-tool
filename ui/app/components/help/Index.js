import React from "react";
import { Link } from "react-router-dom";
import { Jumbotron, Panel, Row, Col } from "react-bootstrap";

export default () =>
  <div className="help">
    <Jumbotron className="hero center">
      <h1>Welcome</h1>
      <p>
        The Export Tool creates up-to-date OSM extracts in various file formats.
        Learn more about the Export Tool below.
      </p>
    </Jumbotron>
    <section className="helpItems">
      <div className="helpItemsBody">
        <Row>
          <Col sm={4} className="itemWrapper">
            <Panel>
              <h2>
                <Link to="/help/quick_start">Quick Start</Link>
              </h2>
              <p>
                First time using the Export Tool? Use this guide to get started.
              </p>
              <Link className="btn btn-default" to="/help/quick_start">
                View
              </Link>
            </Panel>
          </Col>
          <Col sm={4} className="itemWrapper">
            <Panel>
              <h2>
                <Link to="/help/browsing_exports">Browsing Exports</Link>
              </h2>
              <p>
                Learn to browse, run and clone exports already created by other
                users and humanitarian organizations.
              </p>
              <Link className="btn btn-default" to="/help/browsing_exports">
                View
              </Link>
            </Panel>
          </Col>
          <Col sm={4} className="itemWrapper">
            <Panel>
              <h2>
                <Link to="/help/feature_selections">Selecting Features</Link>
              </h2>
              <p>
                How to specify what features are selected by the Export Tool.
              </p>
              <ul>
                <li>Tag Tree</li>
                <li>Storing Configurations</li>
              </ul>
              <Link className="btn btn-default" to="/help/feature_selections">
                View
              </Link>
            </Panel>
          </Col>
        </Row>
        <Row>
          <Col sm={4} className="itemWrapper">
            <Panel>
              <h2>
                <Link to="/help/yaml">YAML Specification</Link>
              </h2>
              <p>Detailed information on the YAML feature selection format.</p>
              <Link className="btn btn-default" to="/help/yaml">
                View
              </Link>
            </Panel>
          </Col>
          <Col sm={4} className="itemWrapper">
            <Panel>
              <h2>
                <Link to="/help/export_formats">File Formats</Link>
              </h2>
              <p>
                Details on file formats available for export from the Export
                Tool.
              </p>
              <ul>
                <li>
                  <Link to="/help/export_formats#shp">
                    Esri Shapefile (.SHP)
                  </Link>
                </li>
                <li>
                  <Link to="/help/export_formats#img">Garmin .IMG</Link>
                </li>
                <li>
                  <Link to="/help/export_formats#kmz">
                    Google Earth KML (.KMZ)
                  </Link>
                </li>
                <li>
                  <Link to="/help/export_formats#pbf">
                    OpenStreetMap Protobuf (.PBF)
                  </Link>
                </li>
                <li>
                  <Link to="/help/export_formats#gpkg">
                    OGC Geopackage (.GPKG)
                  </Link>
                </li>
              </ul>
              <Link className="btn btn-default" to="/help/export_formats">
                View
              </Link>
            </Panel>
          </Col>
          <Col sm={4} className="itemWrapper">
            <Panel>
              <h2>
                <Link to="/help/api">Export Tool API</Link>
              </h2>
              <p>Creating Exports programatically via the JSON API.</p>
              <Link className="btn btn-default" to="/help/api">
                View
              </Link>
            </Panel>
          </Col>
        </Row>
      </div>
    </section>
  </div>;
