import { NonIdealState, Spinner } from "@blueprintjs/core";
import React, { Component } from "react";
import { Col, Row } from "react-bootstrap";
import { FormattedMessage } from "react-intl";
import { connect } from "react-redux";
import { Link } from "react-router-dom";

import ExportRegionPanel from "./ExportRegionPanel";
import FilterForm from "./FilterForm";
import MapListView from "./MapListView";
import Paginator from "./Paginator";
import { getExportRegions } from "../actions/hdx";

class ExportRegionList extends Component {
  render() {
    const { loading, regions } = this.props;

    if (regions == null || Object.keys(regions).length === 0) {
      return null;
    }

    return (
      <div>
        {loading &&
          <NonIdealState
            action={
              <strong>
                <FormattedMessage id="ui.loading" defaultMessage="Loading..." />
              </strong>
            }
            visual={<Spinner />}
          />}
        {loading ||
          Object.entries(regions).map(([id, region], i) => {
            return (
              <Row key={i}>
                <ExportRegionPanel region={region} />
              </Row>
            );
          })}
      </div>
    );
  }
}

export class HDXExportRegionList extends Component {
  state = {
    filters: {}
  };

  componentWillMount() {
    const { getExportRegions } = this.props;

    getExportRegions();
  }

  search = ({ search, ...values }) => {
    const { getExportRegions } = this.props;
    const { filters } = this.state;

    const newFilters = {
      ...filters,
      ...values,
      search
    };

    this.setState({
      filters: newFilters
    });

    return getExportRegions(newFilters);
  };

  render() {
    const {
      hdx,
      hdx: { fetching, selectedExportRegion },
      getExportRegions
    } = this.props;
    const { filters } = this.state;

    const regionGeoms = {
      features: hdx.items.map(x => x.simplified_geom),
      type: "FeatureCollection"
    };

    return (
      <Row style={{ height: "100%" }}>
        <Col xs={6} style={{ height: "100%", overflowY: "scroll" }}>
          <div style={{ padding: "20px" }}>
            <h2 style={{ display: "inline" }}>HDX Export Regions</h2>
            <Link
              to="/hdx/new"
              style={{ float: "right" }}
              className="btn btn-primary"
            >
              Create New Export Region
            </Link>
          </div>
          <div style={{ padding: "20px" }}>
            <FilterForm type="Export Regions" onSubmit={this.search} />
            <hr />
            <Paginator
              collection={hdx}
              getPage={getExportRegions.bind(null, filters)}
            />
            <ExportRegionList regions={hdx.items} loading={fetching} />
            <Paginator
              collection={hdx}
              getPage={getExportRegions.bind(null, filters)}
            />
          </div>
        </Col>
        <Col xs={6} style={{ height: "100%" }}>
          <MapListView
            features={regionGeoms}
            selectedFeatureId={selectedExportRegion}
          />
        </Col>
      </Row>
    );
  }
}

const mapStateToProps = state => {
  return {
    hdx: state.hdx
  };
};

export default connect(mapStateToProps, { getExportRegions })(
  HDXExportRegionList
);
