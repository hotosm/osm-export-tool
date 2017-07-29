import React from "react";
import { ConnectedRouter } from "react-router-redux";
import { Route, Switch } from "react-router-dom";

import {
  ConfigurationList,
  ConfigurationNew,
  ConfigurationDetailContainer
} from "./ConfigurationList";
import { requireAuth } from "./utils";

const AuthorizedConfigurationNew = requireAuth(ConfigurationNew);

export default ({ history }) =>
  <ConnectedRouter history={history}>
    <Switch>
      <Route exact path="/configurations" component={ConfigurationList} />
      <Route
        exact
        path="/configurations/new"
        component={AuthorizedConfigurationNew}
      />
      <Route
        path="/configurations/detail/:uid"
        component={ConfigurationDetailContainer}
      />
    </Switch>
  </ConnectedRouter>;
