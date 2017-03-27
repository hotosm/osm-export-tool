import React from 'react';
import { render } from 'react-dom';
import { createStore } from 'redux'
import { Provider } from 'react-redux';
import { Col,Row } from 'react-bootstrap';

import ExportAOI from './components/ExportAOI'
import HDXCreateForm from './components/HDXCreateForm'
import HDXListForm from './components/HDXListForm'
import HDXEditForm from './components/HDXEditForm'
import rootReducer from './reducers/rootReducer'

var rootElem = document.getElementById('root');

if(rootElem.classList.contains('rootHdxCreate')) {
  var store = createStore(rootReducer);
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
        </Col>
      </Row>,
    rootElem
  )
} else if (rootElem.classList.contains('rootHdxEdit')) {
  var store = createStore(rootReducer);
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
