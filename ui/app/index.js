import React from "react";
import ReactDOM from "react-dom";
import { AppContainer } from "react-hot-loader";
import { Provider } from "react-intl-redux";

import App from "./app";
import store, { history } from "./config/store";

const render = Component =>
  ReactDOM.render(
    <AppContainer>
      <Provider store={store}>
        <Component history={history} />
      </Provider>
    </AppContainer>,
    document.getElementById("root")
  );

if (!global.Intl) {
  require.ensure(["intl", "intl/locale-data/jsonp/en.js"], require => {
    require("intl");
    require("intl/locale-data/jsonp/en.js");
    render(App);
  });
} else {
  render(App);
}

if (module.hot) {
  module.hot.accept("./app", () => render(App));
}
