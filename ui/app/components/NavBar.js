import React from "react";
import { FormattedMessage } from "react-intl";
import { Link } from "react-router-dom";

import hotLogo from "../images/hot_logo.png";

export default () =>
  <div>
    <div id="banner" className="container-fluid">
      <div className="row">
        <div className="col-md-1">
          <img className="logo" src={hotLogo} role="presentation" />
        </div>
        <div className="col-md-3">
          <div id="logotext">
            <FormattedMessage
              id="ui.hot.title"
              defaultMessage="Humanitarian OpenStreetMap Team"
            />
          </div>
        </div>
        <div className="col-md-8">
          <span className="banner-links">
            <a id="id" href="">
              Bahasa Indonesia
            </a>{" "}
            |{" "}
            <a id="de" href="">
              Deutsch
            </a>{" "}
            |{" "}
            <a id="en" href="">
              English
            </a>{" "}
            |{" "}
            <a id="es" href="">
              Español
            </a>{" "}
            |{" "}
            <a id="fr" href="">
              Français
            </a>{" "}
            |{" "}
            <a id="ja" href="">
              日本語
            </a>
          </span>
        </div>
      </div>
    </div>
    <nav className="navbar navbar-inverse">
      <div className="container">
        <div className="navbar-header">
          <button
            type="button"
            className="navbar-toggle collapsed"
            data-toggle="collapse"
            data-target="#navbar"
            aria-expanded="false"
            aria-controls="navbar"
          >
            <span className="sr-only">
              <FormattedMessage
                id="ui.toggle_navigation"
                defaultMessage="Toggle navigation"
              />
            </span>
            <span className="icon-bar" />
            <span className="icon-bar" />
            <span className="icon-bar" />
          </button>
          <Link className="navbar-brand" to="/">
            <strong>
              <FormattedMessage
                id="ui.osm_export_tool.title"
                defaultMessage="OSM Export Tool"
              />
            </strong>
          </Link>
        </div>
        <div id="navbar" className="collapse navbar-collapse">
          <ul className="nav navbar-nav">
            <li>
              <Link to="/exports/new">
                <FormattedMessage id="ui.create" defaultMessage="Create" />
              </Link>
            </li>
            <li>
              <Link to="/exports">
                <FormattedMessage id="ui.exports" defaultMessage="Exports" />
              </Link>
            </li>
            <li>
              <Link to="/configurations">
                <FormattedMessage
                  id="ui.configurations"
                  defaultMessage="Configurations"
                />
              </Link>
            </li>
            <li>
              {/* TODO only link if user has permission */}
              <Link to="/hdx">
                <FormattedMessage id="ui.hdx" defaultMessage="HDX" />
              </Link>
            </li>
            <li>
              <Link to="/help">
                <FormattedMessage id="ui.help" defaultMessage="Help" />
              </Link>
            </li>
            <li>
              <Link to="/about">
                <FormattedMessage id="ui.about" defaultMessage="About" />
              </Link>
            </li>
            <li id="logout">
              <Link to="/logout">
                <span className="glyphicon glyphicon-log-out" />{" "}
                <FormattedMessage id="ui.log_out" defaultMessage="Log Out" />
              </Link>
            </li>
            <li>
              <Link to="/login">
                <FormattedMessage id="ui.log_in" defaultMessage="Log In" />
              </Link>
            </li>
            <li>
              <span className="nav-pad">&nbsp;</span>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  </div>;
