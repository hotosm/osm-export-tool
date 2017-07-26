import React from "react";
import { ConnectedRouter } from "react-router-redux";
import { Route, Switch } from "react-router-dom";

import ExportDetails from "./ExportDetails";
import ExportForm from "./ExportForm";
import ExportList from "./ExportList";
import { requireAuth } from "./utils";

export default ({ history }) =>
  <ConnectedRouter history={history}>
    <Switch>
      <Route
        path="/exports/new/:step?/:featuresUi?"
        component={requireAuth(ExportForm)}
      />
      <Route path="/exports/detail/:id/:run_id?" component={ExportDetails} />
      <Route component={ExportList} />
    </Switch>
  </ConnectedRouter>;
