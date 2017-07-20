import React, { Component } from "react";

import { Button, Col, Row, Table } from "react-bootstrap";
import { connect } from "react-redux";
import { FormattedDate, FormattedTime } from "react-intl";

import FilterForm from "./FilterForm";
import MapListView from "./MapListView";
import Paginator from "./Paginator";
import { getExports } from "../actions/exports";
import { zoomToExportRegion } from "../actions/hdx";

class ExportTable extends Component {
  render() {
    const { jobs, selectRegion } = this.props;

    return (
      <tbody>
        {jobs.map((job, i) =>
          <tr key={i}>
            <td>
              {/* TODO Link */}
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
              <FormattedDate value={job.created_at} />{" "}
              <FormattedTime value={job.created_at} />
            </td>
            <td>
              {job.user.username}
            </td>
            <td>
              <Button
                title="Show on map"
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

  render() {
    const { getExports, jobs, selectedFeatureId, selectRegion } = this.props;
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
          <FilterForm type="Exports" onSubmit={this.search} />
          <hr />
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
          <Paginator
            collection={jobs}
            getPage={getExports.bind(null, filters)}
          />
        </Col>
        <Col xs={6} style={{ height: "100%" }}>
          <MapListView
            features={features}
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
    selectedFeatureId: state.hdx.selectedExportRegion
  };
};

export default connect(mapStateToProps, {
  getExports,
  selectRegion: zoomToExportRegion
})(ExportList);
