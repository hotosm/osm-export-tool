import React from "react";
import { Button } from "react-bootstrap";
import { FormattedMessage } from "react-intl";
import { connect } from "react-redux";
import { Link, NavLink } from "react-router-dom";

import { login, logout } from "../actions/meta";
import hotLogo from "../images/hot_logo.png";
import { selectIsLoggedIn } from "../selectors";
import RequirePermission from "./RequirePermission";

const NavBar = ({ isLoggedIn, login, logout }) =>
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
            <RequirePermission>
              <li>
                <NavLink to="/exports/new">
                  <FormattedMessage id="ui.create" defaultMessage="Create" />
                </NavLink>
              </li>
            </RequirePermission>
            <li>
              <NavLink to="/exports" exact>
                <FormattedMessage id="ui.exports" defaultMessage="Exports" />
              </NavLink>
            </li>
            <li>
              <NavLink to="/configurations">
                <FormattedMessage
                  id="ui.configurations"
                  defaultMessage="Configurations"
                />
              </NavLink>
            </li>
            <RequirePermission
              required={[
                "jobs.add_hdxexportregion",
                "jobs.change_hdxexportregion",
                "jobs.delete_hdxexportregion"
              ]}
            >
              <li>
                {/* TODO only link if user has permission */}
                <NavLink to="/hdx">
                  <FormattedMessage id="ui.hdx" defaultMessage="HDX" />
                </NavLink>
              </li>
            </RequirePermission>
            <li>
              <NavLink to="/help">
                <FormattedMessage id="ui.help" defaultMessage="Help" />
              </NavLink>
            </li>
            <li>
              <NavLink to="/about">
                <FormattedMessage id="ui.about" defaultMessage="About" />
              </NavLink>
            </li>
            {isLoggedIn
              ? <li id="logout">
                  <Button bsStyle="link" onClick={logout}>
                    <span className="glyphicon glyphicon-log-out" />{" "}
                    <FormattedMessage
                      id="ui.log_out"
                      defaultMessage="Log Out"
                    />
                  </Button>
                </li>
              : <li>
                  <Button bsStyle="link" onClick={login}>
                    <FormattedMessage id="ui.log_in" defaultMessage="Log In" />
                  </Button>
                </li>}
            <li>
              <span className="nav-pad">&nbsp;</span>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  </div>;

const mapStateToProps = state => ({
  isLoggedIn: selectIsLoggedIn(state)
});

export default connect(mapStateToProps, { login, logout })(NavBar);
