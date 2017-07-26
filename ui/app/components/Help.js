import React from "react";
import { ConnectedRouter } from "react-router-redux";
import { Route, Switch } from "react-router-dom";

import Index from "./help/Index";
import Create from "./help/Create";
import Exports from "./help/Exports";
import Presets from "./help/Presets";
import FeatureSelection from "./help/FeatureSelection";
import Formats from "./help/Formats";
import Features from "./help/Features";

export default ({ history }) =>
  <ConnectedRouter history={history}>
    <Switch>
      <Route path="/help/create" component={Create} />
      <Route path="/help/exports" component={Exports} />
      <Route path="/help/presets" component={Presets} />
      <Route path="/help/feature_selections" component={FeatureSelection} />
      <Route path="/help/formats" component={Formats} />
      <Route path="/help/features" component={Features} />
      <Route component={Index} />
    </Switch>
  </ConnectedRouter>;
