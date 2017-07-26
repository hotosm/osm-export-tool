import React from "react";
import { ConnectedRouter } from "react-router-redux";
import { Route, Switch } from "react-router-dom";

import HDXExportRegionForm from "./HDXExportRegionForm";
import HDXExportRegionList from "./HDXExportRegionList";
import { requireAuth } from "./utils";

export default ({ history }) =>
  <ConnectedRouter history={history}>
    <Switch>
      <Route path="/hdx/new" component={requireAuth(HDXExportRegionForm)} />
      <Route
        path="/hdx/edit/:id"
        component={requireAuth(HDXExportRegionForm)}
      />
      <Route component={requireAuth(HDXExportRegionList)} />
    </Switch>
  </ConnectedRouter>;
