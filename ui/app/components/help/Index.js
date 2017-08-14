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
                <Link to="/learn/quick_start">Quick Start</Link>
              </h2>
              <p>
                First time using the Export Tool? Use this guide to get started.
              </p>
              <Link className="btn btn-default" to="/learn/quick_start">
                View
              </Link>
            </Panel>
          </Col>
          <Col sm={4} className="itemWrapper">
            <Panel>
              <h2>
                <Link to="/learn/browsing_exports">Browsing Exports</Link>
              </h2>
              <p>
                Learn to browse, run and clone exports already created by other
                users and humanitarian organizations.
              </p>
              <Link className="btn btn-default" to="/learn/browsing_exports">
                View
              </Link>
            </Panel>
          </Col>
          <Col sm={4} className="itemWrapper">
            <Panel>
              <h2>
                <Link to="/learn/feature_selections">Selecting Features</Link>
              </h2>
              <p>
                How to specify what features are selected by the Export Tool.
              </p>
              <ul>
                <li><Link to="/learn/feature_selections/#tagtree">Tag Tree</Link></li>
                <li><Link to="/learn/feature_selections/#configuration">Config File</Link></li>
              </ul>
              <Link className="btn btn-default" to="/learn/feature_selections">
                View
              </Link>
            </Panel>
          </Col>
        </Row>
        <Row>
          <Col sm={4} className="itemWrapper">
            <Panel>
              <h2>
                <Link to="/learn/yaml">YAML Specification</Link>
              </h2>
              <p>Detailed information on the YAML feature selection format.</p>
              <Link className="btn btn-default" to="/learn/yaml">
                View
              </Link>
            </Panel>
          </Col>
          <Col sm={4} className="itemWrapper">
            <Panel>
              <h2>
                <Link to="/learn/export_formats">File Formats</Link>
              </h2>
              <p>
                Details on file formats available for export from the Export
                Tool.
              </p>
              <ul>
                <li>
                  <Link to="/learn/export_formats#shp">
                    Esri Shapefile (.SHP)
                  </Link>
                </li>
                <li>
                  <Link to="/learn/export_formats#gpkg">
                    OGC Geopackage (.GPKG)
                  </Link>
                </li>
                <li>
                  <Link to="/learn/export_formats#img">Garmin (.IMG)</Link>
                </li>
                <li>
                  <Link to="/learn/export_formats#kmz">
                    Google Earth (.KMZ)
                  </Link>
                </li>
                <li>
                  <Link to="/learn/export_formats#xml">
                    OpenStreetMap Source (.XML)
                  </Link>
                </li>
                <li>
                  <Link to="/learn/export_formats#pbf">
                    OpenStreetMap Source (.PBF)
                  </Link>
                </li>
                <li>
                  <Link to="/learn/export_formats#obf">
                    OSMAnd (.OBF)
                  </Link>
                </li>
                <li>
                  <Link to="/learn/export_formats#mwm">
                    maps.me (.MWM)
                  </Link>
                </li>
              </ul>
              <Link className="btn btn-default" to="/learn/export_formats">
                View
              </Link>
            </Panel>
          </Col>
          <Col sm={4} className="itemWrapper">
            <Panel>
              <h2>
                <Link to="/learn/api">Export Tool API</Link>
              </h2>
              <p>Creating Exports programatically via the JSON API.</p>
              <Link className="btn btn-default" to="/learn/api">
                View
              </Link>
            </Panel>
          </Col>
        </Row>
      </div>
    </section>
  </div>;
