import React from "react";
import { Link } from "react-router-dom";
import { Button, Panel } from 'react-bootstrap';

export default () =>
  <div className="help">
    <ol className="breadcrumb">
      <li>
        <Link to="/help">Help</Link>
      </li>
    </ol>
    <h2>How to Use the Export Tool</h2>
    <Panel>
      <h3>Quick Start</h3>
      <p>
        First time using the Export Tool? Use the 
        <Link to="/help/quick_start"> Quick Start Guide</Link>
      </p>
    </Panel>
    <h3>Detailed Help Pages</h3>
    <ul>
      <li>
        <Link to="/help/browsing_exports">Browsing, Running and Cloning existing Exports</Link>
      </li>
      <li>
        <Link to="/help/feature_selections">How Features are Selected</Link>
        <ul>
          <li>
            <Link to="/help/feature_selections#tag_tree">Simple feature selection using the Tag Tree</Link>
          </li>
          <li>
            <Link to="/help/feature_selections#configurations">Storing YAML Feature Selections for Sharing and Re-Use</Link>
          </li>
        </ul>
      </li>
      <li>
        <Link to="/help/yaml">Feature Selection YAML Specification</Link>
      </li>
      <li>
        <Link to="/help/export_formats">Available File Formats for Export</Link>
      </li>
      <li>
        <ul>
          <li>
            <Link to="/help/export_formats#shp">Esri Shapefile (.SHP)</Link>
          </li>
          <li>
            <Link to="/help/export_formats#img">Garmin .IMG</Link>
          </li>
          <li>
            <Link to="/help/export_formats#kmz">Google Earth KML (.KMZ)</Link>
          </li>
          <li>
            <Link to="/help/export_formats#pbf">OpenStreetMap Protobuf (.PBF)</Link>
          </li>
          <li>
            <Link to="/help/export_formats#gpkg">OGC Geopackage (.GPKG)</Link>
          </li>
        </ul>
      </li>
    </ul>
  </div>;
