import React from "react";
import { FormattedMessage } from "react-intl";
import { Link } from "react-router-dom";

export default () =>
  <div className="row">
    <div className="col-md-6">
      <div id="about">
        <h2>
          <FormattedMessage
            id="ui.about.title"
            defaultMessage="Fresh Humanitarian Maps"
          />
        </h2>
        <h3>
          Download up-to-date humanitarian maps for GIS analysis or for use in
          GPS devices and Smartphones.
        </h3>
        <p>
          This platform allows you to create custom OpenStreetMap (OSM) exports
          for various HOT regions. You can specify an area of interest and a
          list of OSM feature tags for the export. There are a number of file
          formats available for exporting the data in, which includes Esri SHP,
          Garmin IMG, Google KMZ, OSM PBF and SQlite SQL. The OSM data available
          from the Export Tool is updated at one minute intervals.
        </p>
        <h2>How to Get Started</h2>
        <p>
          You can view and search through existing HOT exports at our{" "}
          <Link to="/exports">Exports</Link> page. It is not required to have an
          account to view or search existing exports, however if you would like
          to create a new export please{" "}
          <a href="/osm/login/openstreetmap">Login</a> with your OSM account. If
          this is the first time you have logged into the HOT Export Tool, you
          will be asked to provide a valid email address. More detailed help
          information on how to use the Export Tool is available on our{" "}
          <Link to="/help">Help</Link> page.
        </p>
        <h3>License Information</h3>
        <p>
          Data is copyright OpenStreetMap Contributors,{" "}
          <a href="http://opendatacommons.org/licenses/odbl/1-0/">
            ODbL 1.0 licensed
          </a>.
        </p>
      </div>
    </div>
  </div>;
