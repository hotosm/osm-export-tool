import React from 'react';

import createHistory from 'history/createHashHistory';
import ReactDOM from 'react-dom';
import { Redirect, Route } from 'react-router';
import {
  ConnectedRouter,
  routerReducer,
  routerMiddleware
} from 'react-router-redux';
import { createStore, combineReducers, applyMiddleware } from 'redux';
import { Provider, intlReducer } from 'react-intl-redux';
import thunk from 'redux-thunk';

import ExportForm from './components/ExportForm';
import ExportDetails from './components/ExportDetails';
import ExportList from './components/ExportList';
import HDXExportRegionForm from './components/HDXExportRegionForm';
import HDXExportRegionList from './components/HDXExportRegionList';
import {
  ConfigurationList,
  ConfigurationNew,
  ConfigurationDetailContainer
} from './components/ConfigurationList';
import reducers from './reducers/';

const history = createHistory();

const middleware = [routerMiddleware(history), thunk];

if (process.env.NODE_ENV !== 'production') {
  const { createLogger } = require('redux-logger');

  middleware.push(
    createLogger({
      collapsed: true
    })
  );
}

const store = createStore(
  combineReducers({
    ...reducers,
    intl: intlReducer,
    router: routerReducer
  }),
  applyMiddleware(...middleware)
);

// TODO 403 API responses should redirect to the login page
// TODO 404 API responses should either display a 404 page or redirect to the list
ReactDOM.render(
  <Provider store={store}>
    {/* ConnectedRouter will use the store from Provider automatically */}
    <ConnectedRouter history={history}>
      <div style={{ height: '100%' }}>
        <Route
          path='/'
          exact
          render={props => <Redirect to='/exports/new' />}
        />
        <Route path='/exports/new/:step?/:featuresUi?' component={ExportForm} />
        <Route path='/exports/detail/:id/:run_id?' component={ExportDetails} />
        <Route exact path='/exports' component={ExportList} />
        <Route exact path='/configurations' component={ConfigurationList} />
        <Route exact path='/configurations/new' component={ConfigurationNew} />
        <Route
          path='/configurations/detail/:uid'
          component={ConfigurationDetailContainer}
        />
        <Route exact path='/hdx' component={HDXExportRegionList} />
        <Route path='/hdx/new' component={HDXExportRegionForm} />
        <Route path='/hdx/edit/:id' component={HDXExportRegionForm} />
      </div>
    </ConnectedRouter>
  </Provider>,
  document.getElementById('root')
);
