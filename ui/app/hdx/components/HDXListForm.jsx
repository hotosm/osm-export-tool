import React, { Component } from 'react';

import { Row, Col, Panel, Button } from 'react-bootstrap';
import { connect } from 'react-redux';

import {getExportRegions} from '../actions/hdxActions';

function DatasetList (props) {
  const listItems = props.datasets.map((dataset) =>
    <li key={dataset}><a target='_blank' href={`https://data.humdata.org/dataset/${dataset}`}>{dataset}</a></li>
  );

  return (
    <ul>
      {listItems}
    </ul>
  );
}

const ExportRegionList = (props) => {
  const { regions } = props;

  const listItems = regions.map(region => {
    region.datasets = [
      `${region.dataset_prefix}_admin_boundaries`,
      `${region.dataset_prefix}_buildings`,
      `${region.dataset_prefix}_points_of_interest`,
      `${region.dataset_prefix}_roads`,
      `${region.dataset_prefix}_waterways`
    ];

    return (
      <Row key={region.name}>
        <Panel>
          <Col lg={5}>
            <h4>{region.name || 'Untitled'}</h4>
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
            {/* TODO link directly to the export region */}
            <Button block href='edit' title='Settings'>
              <i className='fa fa-cog' />
            </Button>
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

export class HDXListForm extends Component {
  componentDidMount () {
    const { getExportRegions } = this.props;

    getExportRegions();
  }

  render () {
    const { hdx: { exportRegions } } = this.props;

    return (
      <div style={{padding: '20px'}}>
        <h2 style={{display: 'inline'}}>HDX Export Regions</h2>
        <Button style={{float: 'right'}} bsStyle='primary' bsSize='large' href='create'>
          Create New Export Region
        </Button>
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
)(HDXListForm);
