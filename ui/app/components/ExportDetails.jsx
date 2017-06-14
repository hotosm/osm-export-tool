import React, {Component} from 'react';
import { Row, Col, Panel, Button, Table }  from 'react-bootstrap';
import { connect } from 'react-redux';
import { getExport } from '../actions/exportsActions'
import MapListView from './MapListView';

const Details = ({exportInfo}) => {
    return <Table responsive>
      <tbody>
        <tr>
          <td>Export ID:</td>
          <td colSpan="3">{exportInfo.uid}</td>
        </tr>
        <tr>
          <td>Description:</td>
          <td colSpan="3">{exportInfo.description}</td>
        </tr>
        <tr>
          <td>Project:</td>
          <td colSpan="3">{exportInfo.event}</td>
        </tr>
        <tr>
          <td>Area:</td>
          <td colSpan="3">{exportInfo.area}</td>
        </tr>
        <tr>
          <td>Created at:</td>
          <td colSpan="3">{exportInfo.created_at}</td>
        </tr>
        <tr>
          <td>Created by:</td>
          <td colSpan="3">{exportInfo.user}</td>
        </tr>
        <tr>
          <td>Published:</td>
          <td colSpan="3">{exportInfo.published}</td>
        </tr>
        <tr>
          <td>Export formats:</td>
          <td colSpan="3">{exportInfo.export_formats}</td>
        </tr>
      </tbody>
    </Table>
}

const TaskList = ({tasks}) => {
  return <ul>
    {tasks.map((task,i) => {
      return <li key={i}>
        {task.uid}
      </li>
    })}
  </ul>
}

const RunList = ({runs}) => {
  return <div>
    {runs.map((run,i) => {
      return <div key={i}>
        {run.uid}
        <TaskList tasks={run.tasks}/>
      </div>
    })}
  </div>

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
    const geom = exportInfo ? {'features':[exportInfo.the_geom],'type':'FeatureCollection'} : null
    const selectedId = exportInfo ? exportInfo.the_geom.id : null
    return( 
      <Row style={{height: '100%'}}>
        <Col xs={4} style={{height: '100%', padding:"20px", paddingRight:"10px"}}>
          <Panel header="Export Details">
            { exportInfo ? <Details exportInfo={exportInfo}/> : null }
            <Button bsSize="large">Features</Button>
            <Button bsStyle="success" bsSize="large">Re-Run Export</Button>
            <Button bsStyle="primary" bsSize="large">Clone Export</Button>
          </Panel>
        </Col>
        <Col xs={4} style={{height: '100%', padding:"20px", paddingLeft:"10px"}}>
          <Panel header="Export Runs">
          { exportInfo ? <RunList runs={exportInfo.runs}/> : null }
          </Panel>
        </Col>
        <Col xs={4} style={{height: '100%'}}>
          <MapListView features={geom} selectedFeatureId={selectedId}/>
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

