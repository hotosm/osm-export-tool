import React, { Component } from "react";
import {
  Alert,
  Button,
  ButtonGroup,
  Col,
  Modal,
  Panel,
  Row,
  Table
} from "react-bootstrap";
import { FormattedMessage } from "react-intl";
import { connect } from "react-redux";

import MapListView from "./MapListView";
import { getExport, getRuns, runExport, cloneExport } from "../actions/exports";
import { exportFormatNicename, formatDate, formatDuration } from "./utils";

const Details = ({ exportInfo }) => {
  return (
    <Table responsive>
      <tbody>
        <tr>
          <td>
            <FormattedMessage
              id="export.description.label"
              defaultMessage="Description"
            />:
          </td>
          <td colSpan="3">{exportInfo.description}</td>
        </tr>
        <tr>
          <td>
            <FormattedMessage
              id="export.project.label"
              defaultMessage="Project"
            />:
          </td>
          <td colSpan="3">
            {exportInfo.event}
          </td>
        </tr>
        <tr>
          <td>
            <FormattedMessage id="export.area.label" defaultMessage="Area" />:
          </td>
          <td colSpan="3">
            <FormattedMessage
              id="export.area"
              defaultMessage="{area} sq km"
              values={{ area: exportInfo.area }}
            />
          </td>
        </tr>
        <tr>
          <td>
            <FormattedMessage
              id="export.created_at.label"
              defaultMessage="Created at"
            />:
          </td>
          <td colSpan="3">
            {formatDate(exportInfo.created_at)}
          </td>
        </tr>
        <tr>
          <td>
            <FormattedMessage
              id="export.created_by.label"
              defaultMessage="Created by"
            />:
          </td>
          <td colSpan="3">
            {exportInfo.user.username}
          </td>
        </tr>
        <tr>
          <td>
            <FormattedMessage
              id="export.published.label"
              defaultMessage="Published"
            />:
          </td>
          <td colSpan="3">
            {exportInfo.published
              ? <FormattedMessage id="yes" defaultMessage="Yes" />
              : <FormattedMessage id="no" defaultMessage="No" />}
          </td>
        </tr>
        <tr>
          <td>
            <FormattedMessage
              id="export.export_formats.label"
              defaultMessage="Export formats"
            />:
          </td>
          <td colSpan="3">
            {exportInfo.export_formats
              .map(x => exportFormatNicename(x))
              .join(", ")}
          </td>
        </tr>
        <tr>
          <td>
            <FormattedMessage
              id="export.osma.label"
              defaultMessage="OSM Analytics"
            />:
          </td>
          <td colSpan="3">
            <a href={exportInfo.osma_link} target="_blank">
              <FormattedMessage
                id="ui.view_this_area"
                defaultMessage="View this area"
              />
            </a>
          </td>
        </tr>
      </tbody>
    </Table>
  );
};

class ExportRuns extends Component {
  componentWillMount() {
    const { getRuns, jobUid } = this.props;

    getRuns(jobUid);
  }

  componentDidUpdate(prevProps) {
    const { getRuns, jobUid, runs } = this.props;

    if (prevProps.jobUid !== jobUid) {
      clearInterval(this.poller);
      getRuns(jobUid);
    } else {
      if (runs.length > 0) {
        if (runs[0].status === "FAILED" || runs[0].status === "COMPLETED") {
          clearInterval(this.poller);
        } else {
          this.poller = setInterval(() => getRuns(jobUid), 15e3);
        }
      }
    }
  }

  componentWillUnmount() {
    clearInterval(this.poller);
  }

  render() {
    const runs = this.props.runs;
    return (
      <div>
        {runs.map((run, i) => {
          return (
            <Panel header={"Run #" + run.uid} key={i}>
              <Table responsive>
                <tbody>
                  <tr>
                    <td>
                      <FormattedMessage
                        id="ui.exports.status"
                        defaultMessage="Status:"
                      />
                    </td>
                    <td colSpan="3">
                      <Alert bsStyle="success" style={{ marginBottom: "0px" }}>
                        {run.status}
                      </Alert>
                    </td>
                  </tr>
                  <tr>
                    <td>
                      <FormattedMessage
                        id="ui.exports.started"
                        defaultMessage="Started:"
                      />
                    </td>
                    <td colSpan="3">
                      {formatDate(run.started_at)}
                    </td>
                  </tr>
                  <tr>
                    <td>
                      <FormattedMessage
                        id="ui.exports.finished"
                        defaultMessage="Finished:"
                      />
                    </td>
                    <td colSpan="3">
                      {run.finished_at ? formatDate(run.finished_at) : ""}
                    </td>
                  </tr>
                  <tr>
                    <td>
                      <FormattedMessage
                        id="ui.exports.duration"
                        defaultMessage="Duration:"
                      />
                    </td>
                    <td colSpan="3">
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
                                style={{ display: "block" }}
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
  {
    getRuns
  }
)(ExportRuns);

export class ExportDetails extends Component {
  constructor(props) {
    super(props);
    this.state = { showModal: false };
  }

  componentWillMount() {
    const { getExport, match: { params: { id } } } = this.props;
    getExport(id);
  }

  closeModal = () => {
    this.setState({ showModal: false });
  };

  showModal = () => {
    this.setState({ showModal: true });
  };

  render() {
    const {
      cloneExport,
      exportInfo,
      match: { params: { id } },
      runExport
    } = this.props;
    const geom = exportInfo
      ? { features: [exportInfo.simplified_geom], type: "FeatureCollection" }
      : null;
    const selectedId = exportInfo ? exportInfo.simplified_geom.id : null;
    return (
      <Row style={{ height: "100%" }}>
        <Col
          xs={4}
          style={{ height: "100%", padding: "20px", paddingRight: "10px" }}
        >
          <Panel header={exportInfo ? "Export #" + exportInfo.uid : null}>
            {exportInfo ? <Details exportInfo={exportInfo} /> : null}
            <ButtonGroup>
              <Button bsSize="large" onClick={this.showModal}>
                <FormattedMessage
                  id="ui.exports.features"
                  defaultMessage="Features"
                />
              </Button>
              <Button
                bsStyle="success"
                bsSize="large"
                onClick={() => runExport(id)}
              >
                <FormattedMessage
                  id="ui.exports.rerun_export"
                  defaultMessage="Re-Run Export"
                />
              </Button>
              <Button
                bsStyle="primary"
                bsSize="large"
                onClick={() => cloneExport(exportInfo)}
                {...(exportInfo ? {} : { disabled: true })}
              >
                <FormattedMessage
                  id="ui.exports.clone_export"
                  defaultMessage="Clone Export"
                />
              </Button>
            </ButtonGroup>
          </Panel>
        </Col>
        <Col
          xs={4}
          style={{
            height: "100%",
            padding: "20px",
            paddingLeft: "10px",
            overflowY: "scroll"
          }}
        >
          {exportInfo ? <ExportRunsContainer jobUid={id} /> : null}
        </Col>
        <Col xs={4} style={{ height: "100%" }}>
          <MapListView features={geom} selectedFeatureId={selectedId} />
        </Col>
        <Modal show={this.state.showModal} onHide={this.closeModal}>
          <Modal.Header closeButton>
            <Modal.Title>
              <FormattedMessage
                id="ui.exports.feature_selection.title"
                defaultMessage="Feature Selection"
              />
            </Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <pre>
              {exportInfo ? exportInfo.feature_selection : ""}
            </pre>
          </Modal.Body>
          <Modal.Footer>
            <Button onClick={this.closeModal}>
              <FormattedMessage id="ui.close" defaultMessage="Close" />
            </Button>
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

export default connect(mapStateToProps, {
  cloneExport,
  getExport,
  runExport
})(ExportDetails);
