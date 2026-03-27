import area from "@turf/area";
import axios from "axios";
import bbox from "@turf/bbox";
import React, { Component } from "react";
import { Col, Nav, Panel, Row } from "react-bootstrap";
import { FormattedNumber, FormattedMessage } from "react-intl";
import { connect } from "react-redux";
import { Redirect, Route, Switch } from "react-router";
import { NavLink } from "react-router-dom";
import { Fields, formValueSelector, reduxForm } from "redux-form";
import { pointToTile } from "tilebelt";
import ChooseFormats from "./ChooseFormats";
import DescribeExport from "./DescribeExport";
import ExportAOIField from "./ExportAOIField";
import SelectFeatures from "./SelectFeatures";
import Summary from "./Summary";
import { getConfigurations } from "../actions/configurations";
import { createExport, getOverpassTimestamp, getGalaxyTimestamp} from "../actions/exports";
import {
  PresetParser,
  REQUIRES_FEATURE_SELECTION,
  REQUIRES_TILE_SOURCE
} from "./utils";
import { TreeTag, TreeTagYAML } from "../utils/TreeTag";
import { TAGTREE, TAGLOOKUP } from "../utils/TreeTagSettings";

const MAX_AREA = 3000000;
const MAX_TILE_COUNT = 5000;

const form = reduxForm({
  form: "ExportForm",
  onSubmit: (values, dispatch, { createExport }) => {
    console.log("Submitting form. Values:", values);

    if (values.bundle && !values.export_formats.includes("bundle")) {
      // only add bundle format if it wasn't already included
      values.export_formats.push("bundle");
    } else {
      // remove bundle format
      values.export_formats = values.export_formats.filter(x => x !== "bundle");
    }

    createExport(values, "ExportForm");
  },
  validate: ({
    export_formats,
    mbtiles_maxzoom,
    mbtiles_minzoom,
    mbtiles_source,
    the_geom
  }) => {
    const errors = {};

    if (the_geom != null) {
      const areaSqkm = Math.round(area(the_geom) / (1000 * 1000));

      if (areaSqkm > MAX_AREA) {
        errors.the_geom = (
          <FormattedMessage
            id="export.errors.the_geom.too_large"
            defaultMessage="The bounds of this polygon are too large: {areaSqkm} km², max {maxAreaSqkm} km²"
            description="Error message to display when bounds are too large"
            values={{
              areaSqkm: <FormattedNumber value={areaSqkm} />,
              maxAreaSqkm: <FormattedNumber value={MAX_AREA} />
            }}
          />
        );
      }
    }

    if (export_formats.includes("mbtiles") && mbtiles_source == null) {
      errors.mbtiles_source = (
        <FormattedMessage
          id="export.errors.mbtiles.source_required"
          defaultMessage="A source is required when generating an MBTiles archive."
        />
      );
    }

    if (mbtiles_source != null && (mbtiles_maxzoom == null || mbtiles_minzoom == null)) {
      errors.mbtiles_source = <FormattedMessage
        id="export.errors.mbtiles.maxzoom_required"
        defaultMessage="A zoom range must be provided when generating an MBTiles archive."
      />;
    }

    if (mbtiles_source != null && the_geom != null) {
      const bounds = bbox(the_geom);
      let tileCount = 0;

      for (let z = mbtiles_minzoom; z <= mbtiles_maxzoom; z++) {
        const sw = pointToTile(...bounds.slice(0, 2), z);
        const ne = pointToTile(...bounds.slice(2, 4), z);

        const width = 1 + ne[0] - sw[0];
        const height = 1 + sw[1] - ne[1];

        tileCount += width * height;
      }

      if (tileCount > MAX_TILE_COUNT) {
        errors.mbtiles_source = (
          <FormattedMessage
            id="export.errors.mbtiles.too_many"
            defaultMessage="{tileCount} tiles would be rendered; please reduce the zoom range, the size of your AOI, or split the export into pieces covering specific areas in order to render fewer than {maxTileCount} in each."
            description="Error message to display when too many tiles will be rendered"
            values={{
              tileCount: <FormattedNumber value={tileCount} />,
              maxTileCount: <FormattedNumber value={MAX_TILE_COUNT} />
            }}
          />
        );
      }
    }

    return errors;
  }
});

export class ExportForm extends Component {
  constructor(props) {
    super(props);
    this.tagTree = new TreeTag(TAGTREE);
    this.state = {
      tagTreeData: this.tagTree.visibleData(),
      searchQuery: ""
    };
  }

  async fetchData(geometry) {
    const url = window.RAW_DATA_API_URL + "v1/stats/polygon/";
    try {
      const response = await axios.post(url, {
        geometry: geometry
      }, {
        headers: {"Content-Type": "application/json"}
      });
  
      if (response.data) {

        this.setState({ fetchedInfo: response.data });
      }
    } catch (error) {
      console.error("Failed to fetch summary data", error);
     
    }
  }
  
  componentDidUpdate(prevProps) {
    if (this.props.formValues.the_geom !== prevProps.formValues.the_geom) {
      this.fetchData(this.props.formValues.the_geom);
    }
  }

  renderFetchedInfo() {
    const { fetchedInfo } = this.state;
    if (!this.props.formValues.the_geom) return null;
    if (!fetchedInfo) return null;
  
    // Function to trigger the download of the raw data as a JSON file
    const downloadRawData = () => {
      const filename = "raw_region_summary.json";
      const jsonStr = JSON.stringify(fetchedInfo, null, 4);
      const element = document.createElement('a');
      element.setAttribute('href', 'data:text/json;charset=utf-8,' + encodeURIComponent(jsonStr));
      element.setAttribute('download', filename);
      element.style.display = 'none';
      document.body.appendChild(element);
      element.click();
      document.body.removeChild(element);
    };
  
    return (
      <Panel style={{ marginTop: "10px" }}> 
        <div>
          <div>
            <strong style={{ fontSize: "smaller" }}>Buildings:</strong>
            <p style={{ fontSize: "smaller", textAlign: "justify", margin: "10px 0" }}>
              <FormattedMessage 
                id="export.dc.stats.buildings" 
                defaultMessage="{buildings}" 
                values={{ buildings: fetchedInfo.summary.buildings }}
              />
            </p>
          </div>
          <div>
            <strong style={{ fontSize: "smaller" }}>Roads:</strong>
            <p style={{ fontSize: "smaller", textAlign: "justify", margin: "10px 0" }}>
              <FormattedMessage 
                id="export.dc.stats.roads" 
                defaultMessage="{roads}" 
                values={{ roads: fetchedInfo.summary.roads }}
              />
            </p>
          </div>
          <div style={{ fontSize: "smaller", marginTop: "10px" }}>
            More info: 
            <a href="#" onClick={downloadRawData} style={{ marginLeft: "5px" }}>Download</a>,
            <a href={fetchedInfo.meta.indicators} target="_blank" rel="noopener noreferrer" style={{ marginLeft: "5px" }}>Indicators</a>,
            <a href={fetchedInfo.meta.metrics} target="_blank" rel="noopener noreferrer" style={{ marginLeft: "5px" }}>Metrics</a>
          </div>
        </div>
      </Panel>
    );
  }
  
  
  

  componentWillMount() {
    const { getConfigurations, getOverpassTimestamp, getGalaxyTimestamp} = this.props;

    getConfigurations({
      all: true
    });
    getOverpassTimestamp();
    getGalaxyTimestamp();
  }

  onTreeNodeCollapseChange = node => {
    this.tagTree.onTreeNodeCollapseChange(node);
    this.setState({
      tagTreeData: this.tagTree.visibleData(this.state.searchQuery)
    });
  };

  onTreeNodeCheckChange = node => {
    this.tagTree.onTreeNodeCheckChange(node);
    const y = new TreeTagYAML(TAGLOOKUP, this.tagTree.checkedValues());
    this.props.change("feature_selection", y.dataAsYaml());
    this.setState({
      tagTreeData: this.tagTree.visibleData(this.state.searchQuery)
    });
  };

  onSearchChange = e =>
    this.setState({
      searchQuery: e.target.value,
      tagTreeData: this.tagTree.visibleData(e.target.value)
    });

  clearSearch = e =>
    this.setState({ searchQuery: "", tagTreeData: this.tagTree.visibleData() });

  onDrop = files => {
    const file = files[0];
    const reader = new FileReader();
    reader.onload = () => {
      const data = reader.result;
      const p = new PresetParser(data);
      this.props.change("feature_selection", p.asYAML());
    };
    reader.readAsText(file);
  };

  setFormGeoJSON = geojson => this.props.change("the_geom", geojson);

  render() {
    const {
      error,
      formValues,
      formValues: { export_formats: exportFormats, isClone },
      handleSubmit,
      overpassLastUpdated,
      galaxyLastUpdated,
      submitting
    } = this.props;

    let idx = 0;

    return (
      <Row style={{ height: "100%" }}>
        <form style={{ height: "100%" }}>
          <Col
            xs={6}
            style={{ height: "100%", overflowY: "scroll", padding: "20px" }}
          >
            <Nav bsStyle="tabs" style={{ marginBottom: "20px" }}>
              <li>
                <NavLink to="/exports/new/describe">
                  {++idx}{" "}
                  <FormattedMessage
                    id="ui.exports.describe_export"
                    defaultMessage="Describe"
                  />
                </NavLink>
              </li>
              <li>
                <NavLink to="/exports/new/formats">
                  {++idx}{" "}
                  <FormattedMessage
                    id="ui.exports.choose_formats"
                    defaultMessage="Formats"
                  />
                </NavLink>
              </li>
              <li>
                <NavLink to="/exports/new/select">
                  {++idx}{" "}
                  <FormattedMessage
                    id="ui.exports.select_data"
                    defaultMessage="Data"
                  />
                </NavLink>
              </li>
              <li>
                <NavLink to="/exports/new/summary">
                  {++idx}{" "}
                  <FormattedMessage
                    id="ui.exports.summary"
                    defaultMessage="Summary"
                  />
                </NavLink>
              </li>
            </Nav>
            <Switch>
              <Route
                path="/exports/new"
                exact
                render={props => <Redirect to="/exports/new/describe" />}
              />
              <Route
                path="/exports/new/describe"
                render={props =>
                  <DescribeExport next="/exports/new/formats" {...props} />}
              />
              <Route
                path="/exports/new/select"
                render={props => {
                  return <SelectFeatures
                    next="/exports/new/summary"
                    onDrop={this.onDrop}
                    tagTreeData={this.state.tagTreeData}
                    onSearchChange={this.onSearchChange}
                    clearSearch={this.clearSearch}
                    onTreeNodeCheckChange={this.onTreeNodeCheckChange}
                    onTreeNodeCollapseChange={this.onTreeNodeCollapseChange}
                    labelFilter={this.tagTree.labelFilter}
                    exportFormats={exportFormats}
                    isClone={isClone}
                    {...props}
                  />
                }}
              />
              <Route
                path="/exports/new/formats"
                render={props =>
                  <ChooseFormats
                    next="/exports/new/select"
                  />}
              />
              <Route
                path="/exports/new/summary"
                render={props =>
                  <Summary
                    handleSubmit={handleSubmit}
                    formValues={formValues}
                    error={error}
                    submitting={submitting}
                  />}
              />
            </Switch>
            {this.renderFetchedInfo()}
            <Panel style={{ marginTop: "20px" }}>
              <FormattedMessage
                id="ui.overpass_last_updated"
                defaultMessage="Img/pbf/obf updated  {overpassLastUpdated}, Rest of other formats updated {galaxyLastUpdated} "
                values={{ overpassLastUpdated, galaxyLastUpdated }}
              />
            </Panel>
          </Col>
          <Col xs={6} style={{ height: "100%", overflowY: "scroll" }}>
            <Fields
              names={[
                "the_geom",
                "aoi.description",
                "aoi.geomType",
                "aoi.title"
              ]}
              component={ExportAOIField}
            />
          </Col>
        </form>
      </Row>
    );
  }
}

const mapStateToProps = state => {
  return {
    aoiInfo: state.aoiInfo,
    formValues: formValueSelector("ExportForm")(
      state,
      "description",
      "export_formats",
      "isClone",
      "event",
      "name",
      "the_geom"
    ),
    overpassLastUpdated: state.overpassLastUpdated,
    galaxyLastUpdated: state.galaxyLastUpdated,
    initialValues: {
      published: true,
      feature_selection: `
buildings:
    types:
        - lines
        - polygons
    select:
        - name
        - building
    where: building IS NOT NULL
      `.trim(),
      export_formats: ["geojson"]
    }
  };
};

export default connect(mapStateToProps, {
  createExport,
  getConfigurations,
  getOverpassTimestamp,
  getGalaxyTimestamp
})(form(ExportForm));
