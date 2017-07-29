import React from "react";
import { ConnectedRouter } from "react-router-redux";
import { Route, Switch } from "react-router-dom";

import HDXExportRegionForm from "./HDXExportRegionForm";
import HDXExportRegionList from "./HDXExportRegionList";
import RequirePermission from "./RequirePermission";

export default ({ history }) =>
  <RequirePermission
    required={[
      "jobs.add_hdxexportregion",
      "jobs.change_hdxexportregion",
      "jobs.delete_hdxexportregion"
    ]}
  >
    <ConnectedRouter history={history}>
      <Switch>
        <Route path="/hdx/new" component={HDXExportRegionForm} />
        <Route path="/hdx/edit/:id" component={HDXExportRegionForm} />
        <Route component={HDXExportRegionList} />
      </Switch>
    </ConnectedRouter>
  </RequirePermission>;
