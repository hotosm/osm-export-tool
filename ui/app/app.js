import React from "react";
import { Route, Switch } from "react-router";
import { ConnectedRouter } from "react-router-redux";

import About from "./components/About";
import Auth from "./components/Auth";
import Authorized from "./components/Authorized"
import Configurations from "./components/Configurations";
import Exports from "./components/Exports";
import HDX from "./components/HDX";
import Help from "./components/Help";
import Home from "./components/Home";
import NavBar from "./components/NavBar";
import { requireAuth } from "./components/utils";

import "bootstrap/dist/css/bootstrap.css";
import "font-awesome/css/font-awesome.css";
import "./css/style.css";
import "./css/materialIcons.css";
import "./css/ol.css";

export default ({ history }) =>
  <ConnectedRouter history={history}>
    <div style={{ height: "100%" }}>
      <Auth />
      <NavBar />
      <Switch>
        <Route path="/about" component={About} />
        <Route path="/authorized" component={Authorized} />
        <Route path="/configurations" component={Configurations} />
        <Route path="/exports" component={Exports} />
        <Route path="/hdx" component={requireAuth(HDX)} />
        <Route path="/help" component={Help} />
        <Route component={Home} />
      </Switch>
    </div>
  </ConnectedRouter>;
