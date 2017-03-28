import React from 'react';
import { render } from 'react-dom';
import configureStore from './store/configureStore';
import { Provider } from 'react-redux';
import { Col,Row } from 'react-bootstrap';

import ExportAOI from './components/ExportAOI'
import MapListView from './components/MapListView'
import HDXCreateForm from './components/HDXCreateForm'
import HDXListForm from './components/HDXListForm'
import HDXEditForm from './components/HDXEditForm'
import rootReducer from './reducers/rootReducer'

var rootElem = document.getElementById('root');

const store = configureStore();

if(rootElem.classList.contains('rootHdxCreate')) {
  render(
    <Provider store={store}>
      <Row style={{height:'100%'}}>
        <Col xs={6} style={{'height':'100%','overflowY':'scroll'}}>
          <HDXCreateForm/>
        </Col>
        <Col xs={6} style={{'height':'100%'}}>
          <ExportAOI/>
        </Col>
      </Row>
    </Provider>,
    rootElem
  )
} else if (rootElem.classList.contains('rootHdxList')) {
  render(
      <Row style={{height:'100%'}}>
        <Col xs={6} style={{'height':'100%','overflowY':'scroll'}}>
          <HDXListForm/>
        </Col>
        <Col xs={6} style={{'height':'100%'}}>
          <MapListView/>
        </Col>
      </Row>,
    rootElem
  )
} else if (rootElem.classList.contains('rootHdxEdit')) {
  render(
    <Provider store={store}>
      <Row style={{height:'100%'}}>
        <Col xs={6} style={{'height':'100%','overflowY':'scroll'}}>
          <HDXEditForm/>
        </Col>
        <Col xs={6} style={{'height':'100%'}}>
          <ExportAOI/>
        </Col>
      </Row>
    </Provider>,
    rootElem
  )
}
