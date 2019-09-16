import React from "react";
import { ConnectedRouter } from "react-router-redux";
import { Route, Switch } from "react-router-dom";

import PartnerExportRegionForm from "./PartnerExportRegionForm";
import PartnerExportRegionList from "./PartnerExportRegionList";

export default ({ history }) =>
    <ConnectedRouter history={history}>
      <Switch>
         <Route path="/partners/new" component={PartnerExportRegionForm} />
         <Route path="/partners/edit/:id" component={PartnerExportRegionForm} />
        <Route component={PartnerExportRegionList} />
      </Switch>
    </ConnectedRouter>
