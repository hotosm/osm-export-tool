import React from 'react';

import createHistory from 'history/createHashHistory';
import ReactDOM from 'react-dom';
import { Route } from 'react-router';
import { ConnectedRouter, routerReducer, routerMiddleware } from 'react-router-redux';
import { createStore, combineReducers, applyMiddleware } from 'redux';
import { Provider, intlReducer } from 'react-intl-redux';
import createLogger from 'redux-logger';
import thunk from 'redux-thunk';
import { Row } from 'react-bootstrap';

import HDXExportRegionForm from './components/HDXExportRegionForm';
import HDXExportRegionList from './components/HDXExportRegionList';
import ExportForm from './components/ExportForm';
import ExportDetails from './components/ExportDetails';
import PresetToYaml from './components/PresetToYaml';
import reducers from './reducers/';

const history = createHistory();

const store = createStore(
  combineReducers({
    ...reducers,
    intl: intlReducer,
    router: routerReducer
  }),
  applyMiddleware(routerMiddleware(history), thunk, createLogger({
    collapsed: true
  }))
);

// TODO 403 API responses should redirect to the login page
// TODO 404 API responses should either display a 404 page or redirect to the list
ReactDOM.render(
  <Provider store={store}>
    {/* ConnectedRouter will use the store from Provider automatically */}
    <ConnectedRouter history={history}>
        <div style={{height: '100%'}}>
          <Route exact path='/exports/new' component={ExportForm}/>
          <Route path='/exports/:id' component={ExportDetails}/>
          <Route exact path='/hdx' component={HDXExportRegionList} />
          <Route path='/hdx/new' component={HDXExportRegionForm} />
          <Route path='/hdx/edit/:id' component={HDXExportRegionForm} />
          <Route path='/hdx/preset_to_yaml' component={PresetToYaml} />
        </div>
    </ConnectedRouter>
  </Provider>,
  document.getElementById('root')
);
