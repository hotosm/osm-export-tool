import React, { Component } from 'react';

import { Col, Row, Table, Button } from 'react-bootstrap';
import { connect } from 'react-redux';
import MapListView from './MapListView';
import { getExports } from '../actions/exportsActions';
import { zoomToExportRegion } from '../actions/hdxActions';
import { Paginator } from './utils';

class ExportTable extends Component {
  selectRegion = id => this.props.selectRegion(id);

  render () {
    const { jobs } = this.props;

    return (
      <tbody>
        {jobs.map((job, i) => {
          return (
            <tr key={i}>
              <td>
                <a href={`#/exports/detail/${job.uid}`}>
                  {job.name}
                </a>
              </td>
              <td>
                {job.description}
              </td>
              <td>
                {job.project}
              </td>
              <td>
                {job.created_at}
              </td>
              <td>
                {job.user.username}
              </td>
              <td>
                <Button title='Show on map' onClick={() => this.selectRegion(job.simplified_geom.id)}>
                  <i className='fa fa-globe' />
                </Button>
              </td>
            </tr>
          );
        })}
      </tbody>
    );
  }
}

export class ExportList extends Component {
  componentWillMount () {
    this.props.getExports();
  }

  render () {
    const { getExports, jobs, selectedFeatureId, selectRegion } = this.props;

    const features = {
      features: jobs.items.map(j => j.simplified_geom),
      type: 'FeatureCollection'
    };
    return (
      <Row style={{ height: '100%' }}>
        <Col xs={6} style={{ height: '100%', overflowY: 'scroll' }}>
          <div style={{ padding: '20px' }}>
            <h2 style={{ display: 'inline' }}>Exports</h2>
            <Table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Description</th>
                  <th>Project</th>
                  <th>Created At</th>
                  <th>Owner</th>
                  <th />
                </tr>
              </thead>
              <ExportTable jobs={jobs.items} selectRegion={selectRegion} />
            </Table>
            <Paginator collection={jobs} getPage={getExports} />
          </div>
        </Col>
        <Col xs={6} style={{ height: '100%' }}>
          <MapListView features={features} selectedFeatureId={selectedFeatureId} />
        </Col>
      </Row>
    );
  }
}

const mapStateToProps = state => {
  return {
    jobs: state.jobs,
    // TODO NOT HDX
    selectedFeatureId: state.hdx.selectedExportRegion
  };
};

const mapDispatchToProps = dispatch => {
  return {
    getExports: url => dispatch(getExports(url)),
    selectRegion: id => dispatch(zoomToExportRegion(id))
  };
};

export default connect(mapStateToProps, mapDispatchToProps)(ExportList);
