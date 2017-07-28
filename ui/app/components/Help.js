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
      <Route path="/help/api" component={API} />
      <Route path="/help/quick_start" component={QuickStart} />
      <Route path="/help/browsing_exports" component={BrowsingExports} />
      <Route path="/help/feature_selections" component={FeatureSelections} />
      <Route path="/help/yaml" component={Yaml} />
      <Route path="/help/export_formats" component={ExportFormats} />
      <Route component={Index} />
    </Switch>
  </ConnectedRouter>;
