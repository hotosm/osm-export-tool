import React, { Component } from "react";

import { Col, Row } from "react-bootstrap";
import { connect } from "react-redux";
import { Link } from "react-router-dom";

import ExportRegionPanel from "./ExportRegionPanel";
import FilterForm from "./FilterForm";
import MapListView from "./MapListView";
import Paginator from "./Paginator";
import { getExportRegions } from "../actions/hdx";

class ExportRegionList extends Component {
  render() {
    const { regions } = this.props;

    if (regions == null || Object.keys(regions).length === 0) {
      return null;
    }

    return (
      <div>
        {Object.entries(regions).map(([id, region], i) => {
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
      hdx: { selectedExportRegion },
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
              className="btn btn-primary btn-lg"
            >
              Create New Export Region
            </Link>
            <FilterForm type="Export Regions" onSubmit={this.search} />
            <hr />
            <Paginator
              collection={hdx}
              getPage={getExportRegions.bind(null, filters)}
            />
            <ExportRegionList regions={hdx.items} />
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
