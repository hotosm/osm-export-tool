import React from "react";
import { Redirect, Route, Switch } from "react-router";
import { ConnectedRouter } from "react-router-redux";

import About from "./components/About";
import Help from "./components/Help";
import Auth from "./components/Auth";
import ExportForm from "./components/ExportForm";
import ExportDetails from "./components/ExportDetails";
import ExportList from "./components/ExportList";
import HDXExportRegionForm from "./components/HDXExportRegionForm";
import HDXExportRegionList from "./components/HDXExportRegionList";
import {
  ConfigurationList,
  ConfigurationNew,
  ConfigurationDetailContainer
} from "./components/ConfigurationList";
import Home from "./components/Home";
import NavBar from "./components/NavBar";
import { requireAuth } from "./components/utils";

import "bootstrap/dist/css/bootstrap.css";
import "font-awesome/css/font-awesome.css";
import "./css/style.css";
import "./css/materialIcons.css";
import "./css/ol.css";

export default ({ history }) =>
  <ConnectedRouter history={history}>
    <div style={{ height: "100%" }}>
      <Auth />
      <NavBar />
      <Switch>
        <Route exact path="/:lang?/home" component={Home} />
        <Route path="/" exact render={() => <Redirect to="/exports/new" />} />
        <Route
          path="/exports/new/:step?/:featuresUi?"
          component={requireAuth(ExportForm)}
        />
        <Route path="/exports/detail/:id/:run_id?" component={ExportDetails} />
        <Route path="/exports" component={ExportList} />
        <Route
          exact
          path="/configurations"
          component={requireAuth(ConfigurationList)}
        />
        <Route
          exact
          path="/configurations/new"
          component={requireAuth(ConfigurationNew)}
        />
        <Route
          path="/configurations/detail/:uid"
          component={requireAuth(ConfigurationDetailContainer)}
        />
        <Route path="/hdx/new" component={requireAuth(HDXExportRegionForm)} />
        <Route
          path="/hdx/edit/:id"
          component={requireAuth(HDXExportRegionForm)}
        />
        <Route path="/hdx" component={requireAuth(HDXExportRegionList)} />
        <Route path="/about" component={About} />
        <Route path="/help" component={Help} />
      </Switch>
    </div>
  </ConnectedRouter>;
