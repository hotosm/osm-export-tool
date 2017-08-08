import React from "react";
import { ConnectedRouter } from "react-router-redux";
import { Route, Switch } from "react-router-dom";

import API from "./help/API";
import Index from "./help/Index";
import QuickStart from "./help/QuickStart";
import BrowsingExports from "./help/BrowsingExports";
import FeatureSelections from "./help/FeatureSelections";
import Yaml from "./help/Yaml";
import ExportFormats from "./help/ExportFormats";

export default ({ history }) =>
  <ConnectedRouter history={history}>
    <Switch>
      <Route path="/learn/api" component={API} />
      <Route path="/learn/quick_start" component={QuickStart} />
      <Route path="/learn/browsing_exports" component={BrowsingExports} />
      <Route path="/learn/feature_selections" component={FeatureSelections} />
      <Route path="/learn/yaml" component={Yaml} />
      <Route path="/learn/export_formats" component={ExportFormats} />
      <Route component={Index} />
    </Switch>
  </ConnectedRouter>;
