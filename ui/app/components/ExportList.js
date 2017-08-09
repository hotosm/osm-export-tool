import { NonIdealState, Spinner } from "@blueprintjs/core";
import React, { Component } from "react";
import { Button, Col, Row, Table } from "react-bootstrap";
import {
  FormattedDate,
  FormattedMessage,
  FormattedTime,
  defineMessages,
  injectIntl
} from "react-intl";
import { connect } from "react-redux";
import { Link } from "react-router-dom";

import FilterForm from "./FilterForm";
import MapListView from "./MapListView";
import Paginator from "./Paginator";
import { getExports } from "../actions/exports";
import { zoomToExportRegion } from "../actions/hdx";
import { selectStatus } from "../selectors";

const messages = defineMessages({
  exportsType: {
    id: "ui.exports.title",
    defaultMessage: "Exports"
  },
  searchPlaceholder: {
    id: "ui.search.exports.placeholder",
    defaultMessage: "Name, description, event, or username"
  },
  showOnMap: {
    id: "ui.show_on_map",
    defaultMessage: "Show on map"
  }
});

class _ExportTable extends Component {
  render() {
    const { intl: { formatMessage }, jobs, selectRegion } = this.props;

    return (
      <tbody>
        {jobs.map((job, i) =>
          <tr key={i}>
            <td>
              <Link to={`/exports/${job.uid}`}>
                {job.name}
              </Link>
            </td>
            <td>
              {job.description}
            </td>
            <td>
              {job.event}
            </td>
            <td>
              <FormattedDate value={job.created_at} />{" "}
              <FormattedTime value={job.created_at} />
            </td>
            <td>
              {job.user.username}
            </td>
            <td>
              <Button
                title={formatMessage(messages.showOnMap)}
                onClick={() => selectRegion(job.simplified_geom.id)}
              >
                <i className="fa fa-globe" />
              </Button>
            </td>
          </tr>
        )}
      </tbody>
    );
  }
}

const ExportTable = injectIntl(_ExportTable);

export class ExportList extends Component {
  state = {
    filters: {}
  };

  componentWillMount() {
    this.props.getExports();
  }

  search = ({ search, ...values }) => {
    const { getExports } = this.props;
    const { filters } = this.state;

    const newFilters = {
      ...filters,
      ...values,
      search
    };

    this.setState({
      filters: newFilters
    });

    return getExports(newFilters);
  };

  filterByExtent = bbox => {
    const { getExports } = this.props;
    const { filters } = this.state;

    const newFilters = {
      ...filters,
      bbox: bbox.join(",")
    };

    if (bbox.length === 0) {
      delete newFilters.bbox;
    }

    this.setState({
      filters: newFilters
    });

    return getExports(newFilters);
  };

  render() {
    const {
      getExports,
      intl: { formatMessage },
      jobs,
      selectedFeatureId,
      selectRegion,
      status: { loading }
    } = this.props;
    const { filters } = this.state;

    const features = {
      features: jobs.items.map(j => j.simplified_geom),
      type: "FeatureCollection"
    };

    return (
      <Row style={{ height: "100%" }}>
        <Col
          xs={6}
          style={{ height: "100%", overflowY: "scroll", padding: 20 }}
        >
          <h2 style={{ display: "inline" }}>Exports</h2>
          <FilterForm
            searchPlaceholder={messages.searchPlaceholder}
            showDateRange
            type={formatMessage(messages.exportsType)}
            onSubmit={this.search}
          />
          <hr />
          {loading &&
            <div>
              <NonIdealState
                action={
                  <strong>
                    <FormattedMessage
                      id="ui.loading"
                      defaultMessage="Loading..."
                    />"
                  </strong>
                }
                visual={<Spinner />}
              />
            </div>}
          {loading ||
            <div>
              <Table>
                <thead>
                  <tr>
                    <th>
                      <FormattedMessage
                        id="exports.name.label"
                        defaultMessage="Name"
                      />
                    </th>
                    <th>
                      <FormattedMessage
                        id="exports.description.label"
                        defaultMessage="Description"
                      />
                    </th>
                    <th>
                      <FormattedMessage
                        id="exports.project.label"
                        defaultMessage="Project"
                      />
                    </th>
                    <th>
                      <FormattedMessage
                        id="exports.created.label"
                        defaultMessage="Created"
                      />
                    </th>
                    <th>
                      <FormattedMessage
                        id="exports.owner.label"
                        defaultMessage="Owner"
                      />
                    </th>
                    <th />
                  </tr>
                </thead>
                <ExportTable jobs={jobs.items} selectRegion={selectRegion} />
              </Table>
              <Paginator
                collection={jobs}
                getPage={getExports.bind(null, filters)}
              />
            </div>}
        </Col>
        <Col xs={6} style={{ height: "100%" }}>
          <MapListView
            features={features}
            onUpdate={this.filterByExtent}
            selectedFeatureId={selectedFeatureId}
          />
        </Col>
      </Row>
    );
  }
}

const mapStateToProps = state => {
  return {
    jobs: state.jobs,
    // TODO NOT HDX
    selectedFeatureId: state.hdx.selectedExportRegion,
    status: selectStatus(state)
  };
};

export default connect(mapStateToProps, {
  getExports,
  selectRegion: zoomToExportRegion
})(injectIntl(ExportList));
