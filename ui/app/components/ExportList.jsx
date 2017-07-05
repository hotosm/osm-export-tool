import React, { Component } from 'react';

import { Col, Row, Table, Button } from 'react-bootstrap';
import { connect } from 'react-redux';
import MapListView from './MapListView';
import { getExports } from '../actions/exportsActions'
import { Paginator } from './utils'


const ExportTable = ({jobs, selectRegion}) => <tbody>
  {jobs.map((job,i) => {
    return <tr key={i}>
      <td><a href={`#/exports/detail/${job.uid}`}>{job.name}</a></td>
      <td>{job.description}</td>
      <td>{job.project}</td>
      <td>{job.created_at}</td>
      <td>{job.user.username}</td>
      <td>
        <Button>
          <i className='fa fa-globe'/>
        </Button>
      </td>
    </tr>
  })}
</tbody>

export class ExportList extends Component {
  componentDidMount () {
    this.props.getExports()
  }

  render () {
    const { getExports, jobs } = this.props
    const features = {'features':jobs.items.map((j) => j.simplified_geom),'type':'FeatureCollection'}
    return (
      <Row style={{height: '100%'}}>
        <Col xs={6} style={{height: '100%', overflowY: 'scroll'}}>
          <div style={{padding: '20px'}}>
            <h2 style={{display: 'inline'}}>Exports</h2>
            <Table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Description</th>
                  <th>Project</th>
                  <th>Created At</th>
                  <th>Owner</th>
                  <th></th>
                </tr>
              </thead>
              <ExportTable jobs={jobs.items}/>
            </Table>
            <Paginator collection={jobs} getPage={this.props.getExports}/> 
          </div>
        </Col>
        <Col xs={6} style={{height: '100%'}}>
          <MapListView features={features}/>
        </Col>
      </Row>
    );
  }
}

const mapStateToProps = state => {
  return {
    jobs: state.jobs
  };
};

const mapDispatchToProps = dispatch => {
  return {
    getExports: (url) => dispatch(getExports(url))
  };
};

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(ExportList);

