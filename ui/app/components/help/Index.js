import React from "react";
import { Link } from "react-router-dom";

export default () =>
  <div className="help">
    <h2>Help Documentation</h2>

    <div className="well">
      <p>
        The Export Tool allows users to create custom OpenStreetMap (OSM)
        exports for selected HOT regions in various data file formats. The OSM
        data available for download is updated at one minute intervals. This
        help documentation will assist users in navigating the site, and use the
        available functionality effectively to generate OSM exports.
      </p>
    </div>

    <h3>Main Pages</h3>
    <div className="well">
      <p>
        The OSM Export Tool has three main sections; an area to create new
        exports (Create), an area where existing exports are stored and can be
        re-run (Exports), and an area where preset files are stored and can be
        accessed (Presets). The following links will take the user step by step
        through the each section, providing guidance for the available
        functions:
      </p>
      <ul>
        <li>
          <Link to="/help/create">Create</Link>
        </li>
        <li>
          <Link to="/help/exports">Exports</Link>
        </li>
        <li>
          <Link to="/help/presets">Presets (2.0)</Link>
        </li>
        <li>
          <Link to="/help/feature_selections">Feature Selections (3.0)</Link>
        </li>
      </ul>
    </div>

    <h3>File Formats</h3>
    <div className="well">
      <p>
        The OSM Export Tool can download data in five different file formats;
        Esri SHP, Garmin IMG, Google KMZ, OSM PBF and SQlite SQL. The following
        links will provide users with information regarding each file format:
      </p>
      <ul>
        <li>
          <Link to="/help/formats#shp">Esri SHP</Link>
        </li>
        <li>
          <Link to="/help/formats#img">Garmin IMG</Link>
        </li>
        <li>
          <Link to="/help/formats#kmz">Google KMZ</Link>
        </li>
        <li>
          <Link to="/help/formats#pbf">OSM PBF</Link>
        </li>
        <li>
          <Link to="/help/formats#sql">SQlite SQL</Link>
        </li>
      </ul>
    </div>

    <h3>Feature Selection</h3>
    <div className="well">
      <p>
        The OSM Export Tool provides two ways a user can specify which feature
        tags they would like to export from a selected area; either from the
        built-in interactive 'Tree Tag' or load a customised 'Preset File'
        created outside of the tool. This section provides the user guidance on
        how to do both:
      </p>
      <ul>
        <li>
          <Link to="/help/features#tree">Tree Tag</Link>
        </li>
        <li>
          <Link to="/help/features#presets">Preset File</Link>
        </li>
      </ul>
    </div>
  </div>;
