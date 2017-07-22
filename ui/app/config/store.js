import createHistory from "history/createBrowserHistory";
import { intlReducer as intl } from "react-intl-redux";
import { routerReducer as router, routerMiddleware } from "react-router-redux";
import { createStore, combineReducers, applyMiddleware } from "redux";
import { reducer as form } from "redux-form";
import { authMiddleware, authReducer as auth } from "redux-implicit-oauth2";
import thunk from "redux-thunk";

import reducers from "../reducers";

export const history = createHistory();

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
  applyMiddleware(...middleware)
);

export default store;
