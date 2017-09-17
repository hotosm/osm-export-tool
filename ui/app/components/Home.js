import React from "react";
import { Col, Jumbotron, Row } from "react-bootstrap";
import { FormattedMessage } from "react-intl";
import { connect } from "react-redux";
import { Link } from "react-router-dom";

import { login } from "../actions/meta";
import { selectIsLoggedIn } from "../selectors";
import geofabrikLogo from "../images/geofabrik-logo.png";
import usaidLogo from "../images/usaid-logo.png";
import hewlettLogo from "../images/hewlett-logo.png";
import pdcLogo from "../images/pdc-txt-logo.png";
import bnpbLogo from "../images/bnpb-logo.png";

const Home = ({ isLoggedIn, login }) =>
  <div className="home">
    <Jumbotron className="hero center">
      <h1 className="centered">
        <FormattedMessage
          id="ui.title"
          defaultMessage="Download OpenStreetMap Data"
        />
      </h1>
      <p className="centered">
        <FormattedMessage
          id="ui.about.blurb1"
          defaultMessage="The Export Tool is an open service that creates customized extracts of up-to-date OSM data in various file formats."
        />
        <br />
        <FormattedMessage
          id="ui.about.blurb2"
          defaultMessage="Download and use the data simply by crediting the OpenStreetMap contributors."
        />
      </p>
      <p className="centered">
        <Link to="/exports/new" className="btn btn-primary">
          <FormattedMessage
            id="ui.home.action"
            defaultMessage="Start Exporting"
          />
        </Link>
      </p>
    </Jumbotron>
    <Row>
      <Col md={6} mdOffset={3} className="centered">
        <h2>
          <FormattedMessage
            id="ui.about.title.getting_started"
            defaultMessage="Get Started"
          />
        </h2>
        <p>
          <FormattedMessage
            id="ui.about.getting_started.blurb"
            defaultMessage="{signupLink} to start creating exports. Our {quickStartLink} guide will get you using the tool straight away, or read about the Export Tool in more detail through the {learnLink} page."
            values={{
              quickStartLink: (
                <Link to="/learn/quick_start">
                  <FormattedMessage
                    id="ui.quick_start"
                    defaultMessage="Quick Start"
                  />
                </Link>
              ),
              learnLink: (
                <Link to="/learn">
                  <FormattedMessage id="ui.learn" defaultMessage="Learn" />
                </Link>
              ),
              signupLink: (
                <a href="https://www.openstreetmap.org/user/new">
                  <FormattedMessage
                    id="ui.signup"
                    defaultMessage="Sign up for an OSM account"
                  />
                </a>
              )
            }}
          />
        </p>
      </Col>
    </Row>
    <Row style={{ backgroundColor: "#f8f8f8" }}>
      <h2 className="centered">
        <FormattedMessage
          id="ui.about.other_resources"
          defaultMessage="Other Resources"
        />
      </h2>
    </Row>
    <Row style={{ backgroundColor: "#f8f8f8", paddingTop: 0 }}>
      <Col md={4} className="centered">
        <h3>
          <FormattedMessage
            id="ui.about.tasking_manager"
            defaultMessage="HOT Tasking Manager"
          />
        </h3>
        <p>
          <FormattedMessage
            id="ui.about.tasking_manager.blurb"
            defaultMessage="The {tmLink} is used to coordinate and structure large-scale collaborative mapping in OpenStreetMap."
            values={{
              tmLink: (
                <a href="http://tasks.hotosm.org/">
                  <FormattedMessage
                    id="ui.about.tasking_manager.title"
                    defaultMessage="Tasking Manager"
                  />
                </a>
              )
            }}
          />
        </p>
      </Col>
      <Col md={4} className="centered">
        <h3>
          <FormattedMessage
            id="ui.about.osm_analytics"
            defaultMessage="OSM Analytics"
          />
        </h3>
        <p>
          <FormattedMessage
            id="ui.about.other_resources.osma"
            defaultMessage="The {osmaLink} looks at how the world is mapped over time by OpenStreetMap contributors."
            values={{
              osmaLink: (
                <a href="http://osm-analytics.org/">
                  <FormattedMessage
                    id="ui.about.other_resources.osma.title"
                    defaultMessage="Analytics Tool"
                  />
                </a>
              )
            }}
          />
        </p>
      </Col>
      <Col md={4} className="centered">
        <h3>
          <FormattedMessage
            id="ui.about.hdx_platform"
            defaultMessage="HDX Platform"
          />
        </h3>
        <p>
          <FormattedMessage
            id="ui.about.other_resources.hdx"
            defaultMessage="The {hdxLink} hosts OpenStreetMap exports for select countries, updated at regular intervals."
            values={{
              hdxLink: (
                <a href="https://data.humdata.org/">
                  <FormattedMessage
                    id="ui.about.other_resources.hdx_link"
                    defaultMessage="Humanitarian Data Exchange"
                  />
                </a>
              )
            }}
          />
        </p>
      </Col>
    </Row>
    <Row>
      <Col md={6} mdOffset={3} className="centered">
        <h3>
          <FormattedMessage
            id="ui.about.title.license_information"
            defaultMessage="License Information"
          />
        </h3>
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
      </Col>
    </Row>
    <Row>
      <Col md={6} mdOffset={3} className="centered">
        <h3>
          <FormattedMessage
            id="ui.about.title.help"
            defaultMessage="Help Improve the Tool"
          />
        </h3>
        <p>
          <FormattedMessage
            id="ui.about.help"
            defaultMessage="Check out the {githubLink} repository to learn more about the design and how to get involved in the project."
            values={{
              githubLink: (
                <a href="https://github.com/hotosm/osm-export-tool2">
                  <FormattedMessage
                    id="ui.about.github"
                    defaultMessage="GitHub"
                  />
                </a>
              )
            }}
          />
        </p>
      </Col>
    </Row>
    <Row>
      <Col md={6} mdOffset={3} className="centered">
        <h3>
          <FormattedMessage
            id="ui.about.title.partners_and_contributors"
            defaultMessage="Partners and Contributors"
          />
        </h3>
        <p>
          <FormattedMessage
            id="ui.about.partners and contributors"
            defaultMessage="The Export Tool is made possible by many organizations and individuals who contribute time and resources to the project."
          />
        </p>
      </Col>
    </Row>
    <Row>
      <Col md={12} className="centered">
        <a href="https://www.usaid.gov/" style={{ marginRight: 60 }}>
          <img src={usaidLogo} width={200} height={60} />
        </a>
        <a href="https://www.bnpb.go.id/" style={{ marginLeft: 30 }}>
          <img src={bnpbLogo} width={80} height={80} />
        </a>
      </Col>
    </Row>
    <Row>
      <Col md={6} mdOffset={3} className="centered">
        <a href="http://www.pdc.org/">
          <img src={pdcLogo} width={200} height={74} />
        </a>
      </Col>
    </Row>
    <Row>
      <Col md={6} mdOffset={3} className="centered">
        <p>
          <strong>USAID | BNPB | InAWARE</strong>
        </p>
        <p>
          Disaster Management Early Warning and Decision Support Capacity
          Enhancement Project in Indonesia
        </p>
      </Col>
    </Row>
    <Row>
      <Col md={6} mdOffset={3} className="centered">
        <a href="http://www.hewlett.org/">
          <img src={hewlettLogo} width={300} height={64} />
        </a>
      </Col>
    </Row>
    <Row>
      <Col md={6} mdOffset={3} className="centered" style={{ marginBottom:80 }}>
        <a href="https://www.geofabrik.de/">
          <img src={geofabrikLogo} width={200} height={46} />
        </a>
      </Col>
    </Row>
  </div>;

const mapStateToProps = state => ({
  isLoggedIn: selectIsLoggedIn(state)
});

export default connect(mapStateToProps, { login })(Home);
