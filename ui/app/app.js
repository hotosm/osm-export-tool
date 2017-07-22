import React from "react";
import { Redirect, Route } from "react-router";
import { ConnectedRouter } from "react-router-redux";
import { Provider } from "react-intl-redux";

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
import store, { history } from "./config/store";

import "bootstrap/dist/css/bootstrap.css";
import "font-awesome/css/font-awesome.css";
import "./css/style.css";
import "./css/materialIcons.css";
import "./css/ol.css";

const requireAuth = (nextState, replace) => {};

// TODO 403 API responses should redirect to the login page
// TODO 404 API responses should either display a 404 page or redirect to the list
export default () =>
  <Provider store={store}>
    {/* ConnectedRouter will use the store from Provider automatically */}
    <ConnectedRouter history={history}>
      <div style={{ height: "100%" }}>
        <Route exact path="/home" component={Home} />
        <Route path="/" exact render={() => <Redirect to="/exports/new" />} />
        <Route
          path="/exports/new/:step?/:featuresUi?"
          component={ExportForm}
          onEnter={requireAuth}
        />
        <Route path="/exports/detail/:id/:run_id?" component={ExportDetails} />
        <Route exact path="/exports" component={ExportList} />
        <Route exact path="/configurations" component={ConfigurationList} />
        <Route exact path="/configurations/new" component={ConfigurationNew} />
        <Route
          path="/configurations/detail/:uid"
          component={ConfigurationDetailContainer}
        />
        <Route exact path="/hdx" component={HDXExportRegionList} />
        <Route path="/hdx/new" component={HDXExportRegionForm} />
        <Route path="/hdx/edit/:id" component={HDXExportRegionForm} />
      </div>
    </ConnectedRouter>
  </Provider>;
