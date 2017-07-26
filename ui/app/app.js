import React from "react";
import { Redirect, Route } from "react-router";
import { ConnectedRouter } from "react-router-redux";
import { Provider } from "react-intl-redux";

import About from "./components/About";
import Help from "./components/Help";
import HelpCreate from "./components/help/Create";
import HelpExports from "./components/help/Exports";
import HelpPresets from "./components/help/Presets";
import HelpFeatureSelection from "./components/help/FeatureSelection";
import HelpFormats from "./components/help/Formats";
import HelpFeatures from "./components/help/Features";
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
import store, { history } from "./config/store";

import "bootstrap/dist/css/bootstrap.css";
import "font-awesome/css/font-awesome.css";
import "./css/style.css";
import "./css/materialIcons.css";
import "./css/ol.css";

// TODO 403 API responses should redirect to the login page
// TODO 404 API responses should either display a 404 page or redirect to the list
export default () =>
  <Provider store={store}>
    {/* ConnectedRouter will use the store from Provider automatically */}
    <ConnectedRouter history={history}>
      <div style={{ height: "100%" }}>
        <Auth />
        <NavBar />
        <Route exact path="/home" component={Home} />
        <Route path="/" exact render={() => <Redirect to="/exports/new" />} />
        <Route
          path="/exports/new/:step?/:featuresUi?"
          component={requireAuth(ExportForm)}
        />
        <Route path="/exports/detail/:id/:run_id?" component={ExportDetails} />
        <Route exact path="/exports" component={ExportList} />
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
        <Route exact path="/hdx" component={requireAuth(HDXExportRegionList)} />
        <Route path="/hdx/new" component={requireAuth(HDXExportRegionForm)} />
        <Route
          path="/hdx/edit/:id"
          component={requireAuth(HDXExportRegionForm)}
        />
        <Route path="/about" component={About} />
        <Route exact path="/help" component={Help} />
        <Route path="/help/create" component={HelpCreate} />
        <Route path="/help/exports" component={HelpExports} />
        <Route path="/help/presets" component={HelpPresets} />
        <Route
          path="/help/feature_selections"
          component={HelpFeatureSelection}
        />
        <Route path="/help/formats" component={HelpFormats} />
        <Route path="/help/features" component={HelpFeatures} />
      </div>
    </ConnectedRouter>
  </Provider>;
