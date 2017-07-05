import React, { Component } from 'react';
import {
  Alert,
  Button,
  ButtonGroup,
  Col,
  Modal,
  Panel,
  Row,
  Table
} from 'react-bootstrap';
import { connect } from 'react-redux';
import {
  getExport,
  getRuns,
  runExport,
  cloneExport
} from '../actions/exportsActions';
import MapListView from './MapListView';
import { exportFormatNicename, formatDate, formatDuration } from './utils';

const Details = ({ exportInfo }) => {
  return (
    <Table responsive>
      <tbody>
        <tr>
          <td>Description:</td>
          <td colSpan='3'>
            {exportInfo.description}
          </td>
        </tr>
        <tr>
          <td>Project:</td>
          <td colSpan='3'>
            {exportInfo.event}
          </td>
        </tr>
        <tr>
          <td>Area:</td>
          <td colSpan='3'>
            {exportInfo.area} sq km
          </td>
        </tr>
        <tr>
          <td>Created at:</td>
          <td colSpan='3'>
            {formatDate(exportInfo.created_at)}
          </td>
        </tr>
        <tr>
          <td>Created by:</td>
          <td colSpan='3'>
            {exportInfo.user.username}
          </td>
        </tr>
        <tr>
          <td>Published:</td>
          <td colSpan='3'>
            {exportInfo.published ? 'Yes' : 'No'}
          </td>
        </tr>
        <tr>
          <td>Export formats:</td>
          <td colSpan='3'>
            {exportInfo.export_formats
              .map(x => exportFormatNicename(x))
              .join(', ')}
          </td>
        </tr>
        <tr>
          <td>OSM Analytics:</td>
          <td colSpan='3'>
            <a href={exportInfo.osma_link} target='_blank'>
              View this area
            </a>
          </td>
        </tr>
      </tbody>
    </Table>
  );
};

class ExportRuns extends Component {
  componentDidMount () {
    this.props.getRuns(this.props.jobUid);
    this.poller = setInterval(
      () => this.props.getRuns(this.props.jobUid),
      15e3
    );
  }

  componentDidUpdate (prevProps) {
    if (prevProps.jobUid !== this.props.jobUid) {
      clearInterval(this.poller);
      this.poller.getRuns(this.props.jobUid);
    } else {
      if (
        this.props.runs.length > 0 &&
        (this.props.runs[0].status === 'FAILED' ||
          this.props.runs[0].status === 'COMPLETE')
      ) {
        clearInterval(this.poller);
      }
    }
  }

  componentWillUnmount () {
    clearInterval(this.poller);
  }

  render () {
    const runs = this.props.runs;
    return (
      <div>
        {runs.map((run, i) => {
          return (
            <Panel header={'Run #' + run.uid} key={i}>
              <Table responsive>
                <tbody>
                  <tr>
                    <td>Status:</td>
                    <td colSpan='3'>
                      <Alert bsStyle='success' style={{ marginBottom: '0px' }}>
                        {run.status}
                      </Alert>
                    </td>
                  </tr>
                  <tr>
                    <td>Started:</td>
                    <td colSpan='3'>
                      {formatDate(run.started_at)}
                    </td>
                  </tr>
                  <tr>
                    <td>Finished:</td>
                    <td colSpan='3'>
                      {run.finished_at ? formatDate(run.finished_at) : ''}
                    </td>
                  </tr>
                  <tr>
                    <td>Duration:</td>
                    <td colSpan='3'>
                      {formatDuration(run.duration)}
                    </td>
                  </tr>

                  {run.tasks.map((task, i) => {
                    return (
                      <tr key={i}>
                        <td>
                          {exportFormatNicename(task.name)}
                        </td>
                        <td>
                          {task.download_urls.map((dl, j) => {
                            return (
                              <a
                                key={j}
                                style={{ display: 'block' }}
                                href={dl.download_url}
                              >
                                {dl.filename}
                              </a>
                            );
                          })}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </Table>
            </Panel>
          );
        })}
      </div>
    );
  }
}

const ExportRunsContainer = connect(
  state => {
    return {
      runs: state.exportRuns
    };
  },
  dispatch => {
    return {
      getRuns: jobUid => dispatch(getRuns(jobUid))
    };
  }
)(ExportRuns);

export class ExportDetails extends Component {
  constructor (props) {
    super(props);
    this.state = { showModal: false };
  }

  componentWillMount () {
    const { getExport, match: { params: { id } } } = this.props;
    getExport(id);
  }

  handleRun = () => {
    this.props.handleRun(this.props.match.params.id);
  };

  handleClone = () => {
    this.props.handleClone(this.props.exportInfo);
  };

  closeModal = () => {
    this.setState({ showModal: false });
  };

  showModal = () => {
    this.setState({ showModal: true });
  };

  render () {
    const { match: { params: { id } }, exportInfo } = this.props;
    const geom = exportInfo
      ? { features: [exportInfo.simplified_geom], type: 'FeatureCollection' }
      : null;
    const selectedId = exportInfo ? exportInfo.simplified_geom.id : null;
    return (
      <Row style={{ height: '100%' }}>
        <Col
          xs={4}
          style={{ height: '100%', padding: '20px', paddingRight: '10px' }}
        >
          <Panel header={exportInfo ? 'Export #' + exportInfo.uid : null}>
            {exportInfo ? <Details exportInfo={exportInfo} /> : null}
            <ButtonGroup>
              <Button bsSize='large' onClick={this.showModal}>
                Features
              </Button>
              <Button bsStyle='success' bsSize='large' onClick={this.handleRun}>
                Re-Run Export
              </Button>
              <Button
                bsStyle='primary'
                bsSize='large'
                onClick={this.handleClone}
                {...(exportInfo ? {} : { disabled: true })}
              >
                Clone Export
              </Button>
            </ButtonGroup>
          </Panel>
        </Col>
        <Col
          xs={4}
          style={{
            height: '100%',
            padding: '20px',
            paddingLeft: '10px',
            overflowY: 'scroll'
          }}
        >
          {exportInfo ? <ExportRunsContainer jobUid={id} /> : null}
        </Col>
        <Col xs={4} style={{ height: '100%' }}>
          <MapListView features={geom} selectedFeatureId={selectedId} />
        </Col>
        <Modal show={this.state.showModal} onHide={this.closeModal}>
          <Modal.Header closeButton>
            <Modal.Title>Feature Selection</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <pre>
              {exportInfo ? exportInfo.feature_selection : ''}
            </pre>
          </Modal.Body>
          <Modal.Footer>
            <Button onClick={this.closeModal}>Close</Button>
          </Modal.Footer>
        </Modal>
      </Row>
    );
  }
}

const mapStateToProps = state => {
  return {
    exportInfo: state.exportInfo
  };
};

const mapDispatchToProps = dispatch => {
  return {
    getExport: id => dispatch(getExport(id)),
    handleRun: id => dispatch(runExport(id)),
    handleClone: exportInfo => dispatch(cloneExport(exportInfo))
  };
};

export default connect(mapStateToProps, mapDispatchToProps)(ExportDetails);
