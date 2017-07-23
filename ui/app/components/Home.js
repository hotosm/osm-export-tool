import React from "react";
import { Button } from "react-bootstrap";
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
      </div>
    </div>
    <div className="col-md-6">
      <div
        className="panel panel-default"
        style={{ margin: "2em 3em 0em 3em" }}
      >
        <div id="heading-wrap" className="panel-heading">
          <span className="glyphicon-heading glyphicon glyphicon-log-in pull-left">
            &nbsp;
          </span>
          <div>
            <h4>
              <FormattedMessage
                id="ui.login_to_osm"
                defaultMessage="Login to OpenStreetMap"
              />
            </h4>
          </div>
        </div>
        <div className="panel-body">
          <div>
            <div className="row pull-left">
              <div style={{ fontSize: "large" }}>
                If you don't have an OpenStreetMap account you can register for
                one <a href="http://www.openstreetmap.org/user/new">here</a>.
              </div>
              <br />
              <div className="col-md-6">
                <Button bsSize="large" bsStyle="success">
                  <FormattedMessage
                    id="ui.login_to_osm"
                    defaultMessage="Login to OpenStreetMap"
                  />
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>;
