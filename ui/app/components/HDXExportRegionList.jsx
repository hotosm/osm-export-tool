import React, { Component } from 'react';

import { Col, Row } from 'react-bootstrap';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';

import ExportRegionPanel from './ExportRegionPanel';
import { getExportRegions } from '../actions/hdxActions';
import MapListView from './MapListView';

class ExportRegionList extends Component {
  render () {
    const { regions } = this.props;

    if (regions == null || Object.keys(regions).length === 0) {
      return null;
    }

    return (
      <div>
        <hr />
        {Object.entries(regions).map(([id, region], i) => {
          return (
            <Row key={i}>
              <ExportRegionPanel region={region} />
            </Row>
          );
        })}
      </div>
    );
  }
}

export class HDXExportRegionList extends Component {
  componentDidMount () {
    const { getExportRegions } = this.props;

    getExportRegions();
  }

  render () {
    const { hdx: { exportRegions, selectedExportRegion } } = this.props;

    const regionGeoms = {
      features: Object.entries(exportRegions).map(([id, x]) => x.the_geom),
      type: 'FeatureCollection'
    }

    return (
      <Row style={{height: '100%'}}>
        <Col xs={6} style={{height: '100%', overflowY: 'scroll'}}>
          <div style={{padding: '20px'}}>
            <h2 style={{display: 'inline'}}>HDX Export Regions</h2>
            <Link to='/hdx/new' style={{float: 'right'}} className='btn btn-primary btn-lg'>
              Create New Export Region
            </Link>
            <ExportRegionList regions={exportRegions} />
          </div>
        </Col>
        <Col xs={6} style={{height: '100%'}}>
          <MapListView features={regionGeoms} selectedFeatureId={selectedExportRegion}/>
        </Col>
      </Row>
    );
  }
}

const mapStateToProps = state => {
  return {
    hdx: state.hdx
  };
};

const mapDispatchToProps = dispatch => {
  return {
    getExportRegions: () => dispatch(getExportRegions())
  };
};

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(HDXExportRegionList);