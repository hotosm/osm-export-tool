import React, {Component} from 'react';
import { Row, Col, Checkbox, Panel, Button, Table } from 'react-bootstrap';
import { connect } from 'react-redux';
import { getExport } from '../actions/exportsActions'

const Details = ({exportInfo}) => {
    return <ul>
      <li>Job id: {exportInfo.uid}</li>
      <li>Name: {exportInfo.name}</li>
      <li>Description: {exportInfo.description}</li>
      <li>Project: {exportInfo.event}</li>
      <li>Area: {exportInfo.area}</li>
      <li>Created: {exportInfo.created_at}</li>
      <li>Created By: {exportInfo.user}</li>
      <li>Published: {exportInfo.published}</li>
      <li>Export formats: {exportInfo.export_formats}</li>
    </ul>
}

export class ExportDetails extends Component {
  constructor(props) {
      super(props);
  }

  componentDidMount() {
    const { getExport, match: { params: { id }}} = this.props
    getExport(id)
  }

  render() {
    const { exportInfo } = this.props
    console.log(exportInfo)
    return( 
      <Row style={{height: '100%'}}>
        <Col xs={6} style={{height: '100%'}}>
          <Panel>
            <Col xs={6} style={{height: '100%'}}>
              { exportInfo ? <Details exportInfo={exportInfo}/> : null }
              <Button>Features</Button>
              <Button>Re-Run Export</Button>
              <Button>Clone Export</Button>
            </Col>
            <Col xs={6} style={{height: '100%'}}>
              Map
            </Col>
          </Panel>
        </Col>
        <Col xs={6} style={{height: '100%'}}>
          <Panel>
            Runs
          </Panel>
        </Col>
      </Row>)
  }
}

const mapStateToProps = state => {
  return {
    exportInfo: state.exportInfo
  }
}

const mapDispatchToProps = dispatch => {
  return {
    getExport: id => dispatch(getExport(id)),
  }
}

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(ExportDetails);

