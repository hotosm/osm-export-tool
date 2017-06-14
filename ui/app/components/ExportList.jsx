import React, { Component } from 'react';

import { Col, Row } from 'react-bootstrap';
import { connect } from 'react-redux';
import MapListView from './MapListView';


export class ExportList extends Component {
  componentDidMount () {
  }

  render () {
    return (
      <Row style={{height: '100%'}}>
        <Col xs={6} style={{height: '100%', overflowY: 'scroll'}}>
          <div style={{padding: '20px'}}>
            <h2 style={{display: 'inline'}}>Exports</h2>
          </div>
        </Col>
        <Col xs={6} style={{height: '100%'}}>
          <MapListView/>
        </Col>
      </Row>
    );
  }
}

const mapStateToProps = state => {
  return {
  };
};

const mapDispatchToProps = dispatch => {
  return {
  };
};

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(ExportList);

