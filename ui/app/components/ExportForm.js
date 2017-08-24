import area from "@turf/area";
import React, { Component } from "react";
import { Col, Nav, Panel, Row } from "react-bootstrap";
import { FormattedNumber, FormattedMessage } from "react-intl";
import { connect } from "react-redux";
import { Redirect, Route, Switch } from "react-router";
import { NavLink } from "react-router-dom";
import { Fields, formValueSelector, reduxForm } from "redux-form";

import ChooseFormats from "./ChooseFormats";
import DescribeExport from "./DescribeExport";
import ExportAOIField from "./ExportAOIField";
import SelectFeatures from "./SelectFeatures";
import Summary from "./Summary";
import { createExport, getOverpassTimestamp } from "../actions/exports";
import { PresetParser, REQUIRES_FEATURE_SELECTION } from "./utils";
import { TreeTag, TreeTagYAML } from "../utils/TreeTag";
import { TAGTREE, TAGLOOKUP } from "../utils/TreeTagSettings";

const form = reduxForm({
  form: "ExportForm",
  onSubmit: (values, dispatch, { createExport }) => {
    console.log("Submitting form. Values:", values);

    createExport(values, "ExportForm");
  },
  validate: ({ the_geom }) => {
    const errors = {};

    if (the_geom != null) {
      const areaSqkm = Math.round(area(the_geom) / (1000 * 1000));

      const MAX = 3000000;
      if (areaSqkm > MAX) {
        errors.the_geom = (
          <FormattedMessage
            id="export.errors.the_geom.too_large"
            defaultMessage="The bounds of this polygon are too large: {areaSqkm} km², max {maxAreaSqkm} km²"
            description="Error message to display when bounds are too large"
            values={{
              areaSqkm: <FormattedNumber value={areaSqkm} />,
              maxAreaSqkm: <FormattedNumber value={MAX} />
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

  componentWillMount() {
    const { getOverpassTimestamp } = this.props;

    getOverpassTimestamp();
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
      match: { params: { featuresUi } },
      overpassLastUpdated
    } = this.props;

    let idx = 0;

    const requiresFeatureSelection = (exportFormats || [])
      .some(x => REQUIRES_FEATURE_SELECTION[x]);

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
                    defaultMessage="Describe Export"
                  />
                </NavLink>
              </li>
              <li>
                <NavLink to="/exports/new/formats">
                  {++idx}{" "}
                  <FormattedMessage
                    id="ui.exports.choose_formats"
                    defaultMessage="Choose Formats"
                  />
                </NavLink>
              </li>
              {requiresFeatureSelection &&
                <li>
                  <NavLink to="/exports/new/select">
                    {++idx}{" "}
                    <FormattedMessage
                      id="ui.exports.select_features"
                      defaultMessage="Select Features"
                    />
                  </NavLink>
                </li>}
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
                exact
                render={props => {
                  if (isClone) {
                    return <Redirect to="/exports/new/select/yaml" />;
                  }

                  return <Redirect to="/exports/new/select/treetag" />;
                }}
              />
              <Route
                path="/exports/new/select/:featuresUi"
                render={props =>
                  <SelectFeatures
                    next="/exports/new/summary"
                    onDrop={this.onDrop}
                    featuresUi={featuresUi}
                    tagTreeData={this.state.tagTreeData}
                    onSearchChange={this.onSearchChange}
                    clearSearch={this.clearSearch}
                    onTreeNodeCheckChange={this.onTreeNodeCheckChange}
                    onTreeNodeCollapseChange={this.onTreeNodeCollapseChange}
                    labelFilter={this.tagTree.labelFilter}
                    {...props}
                  />}
              />
              <Route
                path="/exports/new/formats"
                render={props =>
                  <ChooseFormats
                    next={
                      requiresFeatureSelection
                        ? "/exports/new/select"
                        : "/exports/new/summary"
                    }
                  />}
              />
              <Route
                path="/exports/new/summary"
                render={props =>
                  <Summary
                    handleSubmit={handleSubmit}
                    formValues={formValues}
                    error={error}
                  />}
              />
            </Switch>
            <Panel style={{ marginTop: "20px" }}>
              <FormattedMessage
                id="ui.overpass_last_updated"
                defaultMessage="OpenStreetMap database last updated {overpassLastUpdated}"
                values={{ overpassLastUpdated }}
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
      export_formats: ["shp"]
    }
  };
};

export default connect(mapStateToProps, {
  createExport,
  getOverpassTimestamp
})(form(ExportForm));
