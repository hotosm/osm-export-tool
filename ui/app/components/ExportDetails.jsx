import React, {Component} from 'react';
import { Row, Col, Panel, Button, Table }  from 'react-bootstrap';
import { connect } from 'react-redux';
import { getExport, getExportRuns, runExport, cloneExport } from '../actions/exportsActions'
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
  return <Table>
    <thead>
      <tr>
        <th>File</th>
        <th>Duration</th>
        <th>Size</th>
      </tr>
    </thead>
    <tbody>
      {tasks.map((task,i) => {
        return <tr key={i}>
          <td><a href={task.download_url}>{task.name}</a></td>
          <td>{task.duration}</td>
          <td>{task.filesize_bytes}</td>
        </tr>
      })}
    </tbody>
  </Table>
}


class ExportRuns extends Component {
  componentDidMount() {
    this.props.getExportRuns(this.props.jobId)
  }

  render() {
    const runs = this.props.runs
    return <div>
      {runs.map((run,i) => {
        return <Table key={i} responsive>
          <tbody>
            <tr>
              <td>Run ID:</td>
              <td colSpan="3">{run.uid}</td>
            </tr>
            <tr>
              <td>Status:</td>
              <td colSpan="3">{run.status}</td>
            </tr>
            <tr>
              <td>Started:</td>
              <td colSpan="3">{run.started_at}</td>
            </tr>
            <tr>
              <td>Finished:</td>
              <td colSpan="3">{run.finished_at}</td>
            </tr>
            <tr>
              <td>Duration:</td>
              <td colSpan="3">{run.duration}</td>
            </tr>
            <tr>
              <td colSpan="4">
                <TaskList tasks={run.tasks}/>
              </td>
            </tr>
          </tbody>
        </Table>
      })}
    </div>
  }
}

const ExportRunsR = connect(
  state => {
    return {
      runs: state.exportRuns
    }
  },
  dispatch => {
    return {
      getExportRuns: id => dispatch(getExportRuns(id)),
    }
  }
)(ExportRuns);


export class ExportDetails extends Component {
  constructor(props) {
      super(props);
  }

  componentDidMount() {
    const { getExport, match: { params: { id }}} = this.props
    getExport(id)
  }

  handleRun = () => {
    this.props.handleRun(this.props.match.params.id)
  }

  handleClone = () => {
    this.props.handleClone(this.props.exportInfo)
  }

  render() {
    const { match: { params: { id }}, exportInfo } = this.props
    const geom = exportInfo ? {'features':[exportInfo.the_geom],'type':'FeatureCollection'} : null
    const selectedId = exportInfo ? exportInfo.the_geom.id : null
    return( 
      <Row style={{height: '100%'}}>
        <Col xs={4} style={{height: '100%', padding:"20px", paddingRight:"10px"}}>
          <Panel header="Export Details">
            { exportInfo ? <Details exportInfo={exportInfo}/> : null }
            <Button bsSize="large">Features</Button>
            <Button bsStyle="success" bsSize="large" onClick={this.handleRun}>Re-Run Export</Button>
            <Button bsStyle="primary" bsSize="large" onClick={this.handleClone} {...exportInfo ? {} : {disabled: true}}>Clone Export</Button>
          </Panel>
        </Col>
        <Col xs={4} style={{height: '100%', padding:"20px", paddingLeft:"10px", overflowY: 'scroll'}}>
          <Panel header="Export Runs">
          { exportInfo ? <ExportRunsR jobId={id}/> : null }
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
    handleRun: id => dispatch(runExport(id)),
    handleClone: (exportInfo) => dispatch(cloneExport(exportInfo))
  }
}

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(ExportDetails);

