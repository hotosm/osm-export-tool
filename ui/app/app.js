import { FocusStyleManager } from "@blueprintjs/core";
import PiwikReactRouter from "piwik-react-router";
import React from "react";
import { addLocaleData } from "react-intl";
import de from "react-intl/locale-data/de";
import en from "react-intl/locale-data/en";
import es from "react-intl/locale-data/es";
import fr from "react-intl/locale-data/fr";
import id from "react-intl/locale-data/id";
import it from "react-intl/locale-data/it";
import pt from "react-intl/locale-data/pt";
import nl from "react-intl/locale-data/nl";
import { IntlProvider } from "react-intl";
import { Route, Switch } from "react-router";
import { ConnectedRouter } from "react-router-redux";

import Auth from "./components/Auth";
import Authorized from "./components/Authorized";
import Configurations from "./components/Configurations";
import Exports from "./components/Exports";
import Footer from "./components/Footer";
import HDX from "./components/HDX";
import Help from "./components/Help";
import Home from "./components/Home";
import NavBar from "./components/NavBar";
import { requireAuth } from "./components/utils";

import "@blueprintjs/core/dist/blueprint.css";
import "@blueprintjs/datetime/dist/blueprint-datetime.css";
import "bootstrap/dist/css/bootstrap.css";
import "font-awesome/css/font-awesome.css";
import "material-design-icons/iconfont/material-icons.css";
import "./css/style.css";
import "./css/ol.css";

const AuthorizedHDX = requireAuth(HDX);

// add locale data for formatting purposes
addLocaleData([...de, ...en, ...es, ...fr, ...id, ...it, ...pt, ...nl]);

FocusStyleManager.onlyShowFocusOnTabs();

export default ({ history }) => {
  if (process.env.NODE_ENV === "production") {
    const piwik = PiwikReactRouter({
      url: "piwik.hotosm.org",
      siteId: 10
    });

    history = piwik.connectToHistory(history);
  }

  return (
    <IntlProvider>
      <ConnectedRouter history={history}>
        <div style={{ height: "100%" }}>
          <Auth />
          <NavBar />
          <Switch>
            <Route path="/authorized" component={Authorized} />
            <Route path="/configurations" component={Configurations} />
            <Route path="/exports" component={Exports} />
            <Route path="/hdx" component={AuthorizedHDX} />
            <Route path="/learn" component={Help} />
            <Route component={Home} />
          </Switch>
          <Footer />
        </div>
      </ConnectedRouter>
    </IntlProvider>
  );
};
