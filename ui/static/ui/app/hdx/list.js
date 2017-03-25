import React from 'react';
import { render } from 'react-dom';
import { createStore } from 'redux'
import { Provider } from 'react-redux';

//import CreateExport from './components/CreateExport'
import ExportAOI from './components/ExportAOI'
import rootReducer from './reducers/rootReducer'

var store = createStore(rootReducer);
console.log(store);

render(
  <Provider store={store}>
    <ExportAOI/>
  </Provider>,
  document.getElementById('root')
)
