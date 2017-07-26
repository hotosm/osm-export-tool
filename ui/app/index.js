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

render(App);

if (module.hot) {
  module.hot.accept("./app", () => render(App));
}
