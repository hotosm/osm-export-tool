import React, { Component } from 'react';

import { Row, Col, Panel, Button } from 'react-bootstrap';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';

import { getExportRegions } from '../actions/hdxActions';

function DatasetList (props) {
  const listItems = props.datasets.map((dataset, i) =>
    <li key={i}><a target='_blank' href={`https://data.humdata.org/dataset/${dataset}`}>{dataset}</a></li>
  );

  return (
    <ul>
      {listItems}
    </ul>
  );
}

const ExportRegionList = (props) => {
  const { regions } = props;

  const listItems = regions.map((region, i) => {
    region.datasets = [
      `${region.dataset_prefix}_admin_boundaries`,
      `${region.dataset_prefix}_buildings`,
      `${region.dataset_prefix}_points_of_interest`,
      `${region.dataset_prefix}_roads`,
      `${region.dataset_prefix}_waterways`
    ];

    return (
      <Row key={i}>
        <Panel>
          <Col lg={5}>
            <h4><Link to={`/edit/${region.id}`}>{region.name || 'Untitled'}</Link></h4>
            <DatasetList datasets={region.datasets} />
          </Col>
          <Col lg={5}>
            Last Run: 2017/03/27 00:00:00PM<br />
            Next Run: none<br />
            Schedule: Every Sunday at 1:00 UTC
          </Col>
          <Col lg={1} md={2}>
            <Button block title='Map'>
              {/* TODO where does this go? */}
              <i className='fa fa-globe' />
            </Button>
          </Col>
          <Col lg={1} md={2}>
            <Link className='btn btn-default btn-block' to={`/edit/${region.dataset_prefix}`} title='Settings'>
              <i className='fa fa-cog' />
            </Link>
          </Col>
        </Panel>
      </Row>
    );
  });

  return (
    <div>
      {listItems}
    </div>
  );
};

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
        <hr />
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
    getExportRegions: () => {
      dispatch(getExportRegions());
    }
  };
};

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(HDXExportRegionList);
