import React, { Component } from 'react';

import { Row } from 'react-bootstrap';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';

import ExportRegionPanel from './ExportRegionPanel';
import { getExportRegions } from '../actions/hdxActions';

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
    const { hdx: { exportRegions } } = this.props;

    return (
      <div style={{padding: '20px'}}>
        <h2 style={{display: 'inline'}}>HDX Export Regions</h2>
        <Link to='/new' style={{float: 'right'}} className='btn btn-primary btn-lg'>
          Create New Export Region
        </Link>
        <ExportRegionList regions={exportRegions} />
      </div>
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
