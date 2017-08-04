import React from "react";
import { Button, Nav, NavItem, Navbar } from "react-bootstrap";
import { FormattedMessage } from "react-intl";
import { connect } from "react-redux";
import { NavLink } from "react-router-dom";

import { login, logout } from "../actions/meta";
import hotLogo from "../images/hot-logo.svg";
import { selectIsLoggedIn } from "../selectors";
import LocaleSelector from "./LocaleSelector";
import RequirePermission from "./RequirePermission";

const NavBar = ({ isLoggedIn, login, logout }) =>
  <Navbar>
    <Navbar.Header>
      <Navbar.Brand>
        <a href="https://www.hotosm.org/">
          <img className="logo" src={hotLogo} role="presentation" />
        </a>
      </Navbar.Brand>
    </Navbar.Header>
    <Nav className="pull-right">
      <li>
        <NavLink to="/">
          <FormattedMessage id="ui.about" defaultMessage="About" />
        </NavLink>
      </li>
      <li>
        <NavLink to="/help">
          <FormattedMessage id="ui.help" defaultMessage="Learn" />
        </NavLink>
      </li>
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
          <NavLink to="/hdx">
            <FormattedMessage id="ui.hdx" defaultMessage="HDX" />
          </NavLink>
        </li>
      </RequirePermission>
      <NavItem>
        <LocaleSelector />
      </NavItem>
      <NavItem>
      {!isLoggedIn &&
        <Button bsStyle="danger" onClick={login}>
          <FormattedMessage id="ui.log_in" defaultMessage="Log In" />
        </Button>}
      {isLoggedIn &&
        <Button bsStyle="danger" onClick={logout}>
          <FormattedMessage id="ui.log_out" defaultMessage="Log Out" />
        </Button>}
      </NavItem>
    </Nav>
  </Navbar>;

const mapStateToProps = state => ({
  isLoggedIn: selectIsLoggedIn(state)
});

export default connect(mapStateToProps, { login, logout })(NavBar);
