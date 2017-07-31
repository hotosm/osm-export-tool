import createHistory from "history/createBrowserHistory";
import { intlReducer as intl } from "react-intl-redux";
import { routerReducer as router, routerMiddleware } from "react-router-redux";
import { createStore, combineReducers, applyMiddleware } from "redux";
import { reducer as form } from "redux-form";
import { authMiddleware, authReducer as auth } from "redux-implicit-oauth2";
import thunk from "redux-thunk";

import reducers from "../reducers";

const loadMessages = locale => {
  try {
    return {
      locale,
      messages: require(`../i18n/locales/${locale}.json`)[locale]
    };
  } catch (err) {
    const lang = locale.split("-")[0];

    if (lang !== locale) {
      return loadMessages(lang);
    }
  }
};

const initialState = {
  intl: loadMessages(navigator.language)
};

const match = window.location.pathname.match(/(\/\w{2})?\/v3/);
let basename = null;

if (match != null) {
  basename = match[0];
}

export const history = createHistory({
  basename
});

const middleware = [thunk, routerMiddleware(history), authMiddleware];

if (process.env.NODE_ENV !== "production") {
  const { createLogger } = require("redux-logger");

  middleware.push(
    createLogger({
      collapsed: true
    })
  );
}

const store = createStore(
  combineReducers({
    ...reducers,
    auth,
    form,
    intl,
    router
  }),
  initialState,
  applyMiddleware(...middleware)
);

export default store;
