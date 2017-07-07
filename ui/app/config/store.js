import createHistory from "history/createHashHistory";
import { intlReducer as intl } from "react-intl-redux";
import {
  routerReducer as router,
  routerMiddleware
} from "react-router-redux";
import { createStore, combineReducers, applyMiddleware } from "redux";
import { reducer as form } from "redux-form";
import thunk from "redux-thunk";

import reducers from "../reducers";

const history = createHistory();

const middleware = [thunk, routerMiddleware(history)];

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
    form,
    intl,
    router
  }),
  applyMiddleware(...middleware)
);

export default store;
