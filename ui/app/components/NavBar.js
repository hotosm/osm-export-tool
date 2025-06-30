import React from "react";
import { Button, Nav, NavItem, Navbar } from "react-bootstrap";
import { FormattedMessage } from "react-intl";
import { connect } from "react-redux";
import { Link, NavLink } from "react-router-dom";

import { login, logout } from "../actions/meta";
import hotLogo from "../images/hot-logo.svg";
import { selectIsLoggedIn } from "../selectors";
import LocaleSelector from "./LocaleSelector";
import RequirePermission from "./RequirePermission";

const NavBar = ({ isLoggedIn, login, logout }) => (
  <Navbar>
    <Navbar.Header>
      <Navbar.Brand>
        <Link to="/exports/new">
          <img className="logo" src={hotLogo} role="presentation" />
          <span>Export Tool</span>
        </Link>
      </Navbar.Brand>
    </Navbar.Header>
    <Nav className="pull-right">
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
          <FormattedMessage id="ui.configurations" defaultMessage="Configs" />
        </NavLink>
      </li>
      <RequirePermission
        required={[
          "jobs.add_partnerexportregion",
          "jobs.change_partnerexportregion",
          "jobs.delete_partnerexportregion",
        ]}
      >
        <li>
          <NavLink to="/partners">
            <FormattedMessage id="ui.partners" defaultMessage="Partners" />
          </NavLink>
        </li>
      </RequirePermission>
      <RequirePermission
        required={[
          "jobs.add_hdxexportregion",
          "jobs.change_hdxexportregion",
          "jobs.delete_hdxexportregion",
        ]}
      >
        <li>
          <NavLink to="/hdx">
            <FormattedMessage id="ui.hdx" defaultMessage="HDX" />
          </NavLink>
        </li>
      </RequirePermission>
      <RequirePermission required={["auth.add_user"]}>
        <li>
          <a href="/admin">
            <FormattedMessage id="ui.admin" defaultMessage="Admin" />
          </a>
        </li>
      </RequirePermission>
      <RequirePermission required={["auth.add_user"]}>
        <li>
          <a href="/worker-dashboard/" target="_blank">
            <FormattedMessage id="ui.workers" defaultMessage="Workers" />
          </a>
        </li>

      </RequirePermission>
      <RequirePermission required={["auth.add_user"]}>
        <li>
          <a href="/api/status" target="_blank">
            <FormattedMessage id="ui.machine_status" defaultMessage="Status" />
          </a>
        </li>

      </RequirePermission>
      <RequirePermission required={["auth.add_user"]}>
        <li>
          <NavLink to="/stats">
            <FormattedMessage id="ui.stats" defaultMessage="Stats" />
          </NavLink>
        </li>
      </RequirePermission>
      <li>
        <NavLink to="/">
          <FormattedMessage id="ui.about" defaultMessage="About" />
        </NavLink>
      </li>
      <li>
        <NavLink to="/learn">
          <FormattedMessage id="ui.help" defaultMessage="Learn" />
        </NavLink>
      </li>
      <li>
        <a
          href="https://hotosm.atlassian.net/servicedesk/customer/portal/4"
          target="_blank"
          rel="noopener noreferrer"
        >
          <span title="For technical support click here">
            <FormattedMessage id="ui.support" defaultMessage="Support" />
          </span>
        </a>
      </li>
      <NavItem>
        <LocaleSelector />
      </NavItem>
      <NavItem>
        {!isLoggedIn && (
          <Button bsStyle="danger" onClick={login}>
            <FormattedMessage id="ui.log_in" defaultMessage="Log In" />
          </Button>
        )}
        {isLoggedIn && (
          <Button bsStyle="danger" onClick={logout}>
            <FormattedMessage id="ui.log_out" defaultMessage="Log Out" />
          </Button>
        )}
      </NavItem>
    </Nav>
  </Navbar>
);

const mapStateToProps = (state) => ({
  isLoggedIn: selectIsLoggedIn(state),
});

export default connect(mapStateToProps, { login, logout })(NavBar);
