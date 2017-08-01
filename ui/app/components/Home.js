import React from "react";
import { Button } from "react-bootstrap";
import { FormattedMessage } from "react-intl";
import { connect } from "react-redux";
import { Link } from "react-router-dom";

import { login } from "../actions/meta";
import { selectIsLoggedIn } from "../selectors";

const Home = ({ isLoggedIn, login }) =>
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
            defaultMessage="Download up-to-date humanitarian maps for GIS analysis, GPS devices and Smartphones."
          />
        </h3>
        <p>
          <FormattedMessage
            id="ui.about.overview"
            defaultMessage="The Export Tool creates OpenStreetMap-derived files that can be used seamlessly for GIS and mobile mapping applications. OSM data is updated at one minute intervals. OSM data can be extracted for any polygonal area and filtered to only relevant tags and features."
          />
        </p>
        <h2>
          <FormattedMessage
            id="ui.about.title.getting_started"
            defaultMessage="Get Started"
          />
        </h2>
        <p>
          <FormattedMessage
            id="ui.about.getting_started"
            defaultMessage="Browse through existing exports at our {exportsLink} page without registering an account. An OSM account and valid email address is required to create exports. A guide to the Export Tool is available on our {helpLink} page."
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
        <h2>
          <FormattedMessage
            id="ui.about.other_resources"
            defaultMessage="Other Resources"
          />
        </h2>
        <p>
          <FormattedMessage
            id="ui.about.other_resources.hdx"
            defaultMessage="The {hdxLink} hosts exports for popular regions, updated at regular intervals."
            values={{
              hdxLink: (
                <Link to="https://data.humdata.org/">
                  <FormattedMessage id="ui.about.other_resources.hdx_link" defaultMessage="Humanitarian Data Exchange (HDX)" />
                </Link>
              )
            }}
          />
        </p>
        <p>
          <FormattedMessage
            id="ui.about.other_resources.tm"
            defaultMessage="The {tmLink} coordinates humanitarian mapping efforts."
            values={{
              tmLink: (
                <Link to="http://tasks.hotosm.org/">
                  <FormattedMessage id="ui.about.other_resources.tm_link" defaultMessage="HOT Tasking Manager" />
                </Link>
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
    {!isLoggedIn &&
      <div className="col-md-6">
        <div
          className="panel panel-default"
          style={{ margin: "2em 3em 0em 3em" }}
        >
          <div id="heading-wrap" className="panel-heading">
            <h3>
              <FormattedMessage
                id="ui.login_to_osm"
                defaultMessage="Login to OpenStreetMap"
              />
            </h3>
          </div>
          <div className="panel-body">
            <div>
              <div className="row pull-left">
                <div style={{ fontSize: "large" }}>
                  If you don't have an OpenStreetMap account you can register
                  for one{" "}
                  <a href="http://www.openstreetmap.org/user/new">here</a>.
                </div>
                <br />
                <div className="col-md-6">
                  <Button bsSize="large" bsStyle="success" onClick={login}>
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
      </div>}
  </div>;

const mapStateToProps = state => ({
  isLoggedIn: selectIsLoggedIn(state)
});

export default connect(mapStateToProps, { login })(Home);
