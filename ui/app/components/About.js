import React from "react";
import { FormattedMessage } from "react-intl";
import { Link } from "react-router-dom";

export default () =>
  <div className="row">
    <div className="col-md-6">
      <div id="about">
        <h2>
          <FormattedMessage
            id="ui.about.title.overview"
            defaultMessage="Fresh Humanitarian Maps"
          />
        </h2>
        <h3>
          <FormattedMessage
            id="ui.about.subhead"
            defaultMessage="Download up-to-date humanitarian maps for GIS analysis or for use in GPS devices and Smartphones."
          />
        </h3>
        <p>
          <FormattedMessage
            id="ui.about.overview"
            defaultMessage="This platform allows you to create custom OpenStreetMap (OSM) exports for various HOT regions. You can specify an area of interest and a list of OSM feature tags for the export. There are a number of file formats available for exporting the data in, which includes Esri SHP, Garmin IMG, Google KMZ, OSM PBF and SQlite SQL. The OSM data available from the Export Tool is updated at one minute intervals."
          />
        </p>
        <h2>
          <FormattedMessage
            id="ui.about.title.getting_started"
            defaultMessage="How to Get Started"
          />
        </h2>
        <p>
          <FormattedMessage
            id="ui.about.getting_started"
            defaultMessage="You can view and search through existing HOT exports at our {exportsLink} page. It is not required to have an account to view or search existing exports, however if you would like to create a new export please {loginLink} with your OSM account. If this is the first time you have logged into the HOT Export Tool, you will be asked to provide a valid email address. More detailed help information on how to use the Export Tool is available on our {helpLink} page."
            values={{
              exportsLink: (
                <Link to="/exports">
                  <FormattedMessage id="ui.exports" defaultMessage="Exports" />
                </Link>
              ),
              helpLink: (
                <Link to="/help">
                  <FormattedMessage id="ui.help" defaultMessage="Help" />
                </Link>
              ),
              loginLink: (
                <a href="/osm/login/openstreetmap">
                  <FormattedMessage id="ui.login" defaultMessage="Login" />
                </a>
              )
            }}
          />
        </p>
        <h3>License Information</h3>
        <p>
          <FormattedMessage
            id="ui.about.license"
            defaultMessage="Data is copyright OpenStreetMap Contributors, {odblLink}."
            values={{
              odblLink: (
                <a href="http://opendatacommons.org/licenses/odbl/1-0">
                  <FormattedMessage
                    id="ui.about.license.odbl"
                    defaultMessage="ODbL 1.0 licensed"
                  />
                </a>
              )
            }}
          />
        </p>
      </div>
    </div>
  </div>;
