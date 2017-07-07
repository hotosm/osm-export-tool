import React, { Component } from "react";
import {
  Nav,
  NavItem,
  InputGroup,
  ButtonGroup,
  Row,
  Col,
  Panel,
  Button,
  FormControl,
  Table
} from "react-bootstrap";
import Dropzone from "react-dropzone";
import { connect } from "react-redux";
import { Redirect, Route, Switch } from "react-router";
import {
  Field,
  Fields,
  formValueSelector,
  reduxForm,
  change
} from "redux-form";
import { push } from "react-router-redux";

import ExportAOIField from "./ExportAOIField";
import TreeMenu from "./react-tree-menu/TreeMenu";
import Paginator from "./Paginator";
import { getConfigurations } from "../actions/configurationActions";
import { createExport, getOverpassTimestamp } from "../actions/exportsActions";
import {
  AVAILABLE_EXPORT_FORMATS,
  getFormatCheckboxes,
  renderCheckboxes,
  renderCheckbox,
  renderInput,
  renderTextArea,
  PresetParser,
  REQUIRES_FEATURE_SELECTION
} from "./utils";
import { TreeTag, TreeTagYAML } from "../utils/TreeTag";
import { TAGTREE, TAGLOOKUP } from "../utils/TreeTagSettings";
import styles from "../styles/ExportForm.css";

const form = reduxForm({
  form: "ExportForm",
  onSubmit: (values, dispatch, props) => {
    console.log("Submitting form. Values:", values);
    dispatch(createExport(values, "ExportForm"));
  }
});

const Describe = ({ next }) =>
  <Row>
    <Field
      name="name"
      type="text"
      label="Name"
      placeholder="name this export"
      component={renderInput}
    />
    <Field
      name="description"
      type="text"
      label="Description"
      component={renderTextArea}
      rows="4"
    />
    <Field
      name="project"
      type="text"
      label="Project"
      placeholder="which activation this export is for"
      component={renderInput}
    />
    <Button bsSize="large" style={{ float: "right" }} onClick={next}>
      Next
    </Button>
  </Row>;

const YamlUi = ({ onDrop }) =>
  <div>
    <Field
      name="feature_selection"
      type="text"
      label="Feature Selection"
      component={renderTextArea}
      className={styles.featureSelection}
      rows="10"
    />
    <Dropzone className="nullClassName" onDrop={onDrop}>
      <Button>Load from JOSM Preset .XML</Button>
    </Dropzone>
  </div>;

class TreeTagUi extends React.Component {
  render() {
    return (
      <div>
        <InputGroup
          style={{ width: "100%", marginTop: "20px", marginBottom: "10px" }}
        >
          <FormControl
            id="treeTagSearch"
            type="text"
            label="treeTagSearch"
            placeholder="Search for a feature type..."
            onChange={this.props.onSearchChange}
          />
          <InputGroup.Button>
            <Button onClick={this.props.clearSearch}>Clear</Button>
          </InputGroup.Button>
        </InputGroup>

        <TreeMenu
          data={this.props.tagTreeData}
          onTreeNodeCollapseChange={this.props.onTreeNodeCollapseChange}
          onTreeNodeCheckChange={this.props.onTreeNodeCheckChange}
          expandIconClass="fa fa-chevron-right"
          collapseIconClass="fa fa-chevron-down"
          labelFilter={this.props.labelFilter}
        />
      </div>
    );
  }
}

class StoredConfComponent extends React.Component {
  componentDidMount() {
    this.props.getConfigurations();
  }

  onClick = yaml => {
    this.props.setYaml(yaml);
    this.props.switchToYaml();
  };

  render() {
    return (
      <div>
        <InputGroup
          style={{ width: "100%", marginTop: "20px", marginBottom: "10px" }}
        >
          <FormControl
            id="storedConfigSearch"
            type="text"
            label="storedConfigSearch"
            placeholder="Search for a configuration..."
          />
          <InputGroup.Button>
            <Button>Clear</Button>
          </InputGroup.Button>
        </InputGroup>
        <Paginator
          collection={this.props.configurations}
          getPage={this.props.getConfigurations}
        />
        <Table>
          <thead>
            <tr>
              <th>name</th>
              <th>description</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {this.props.configurations.items.map((configuration, i) => {
              return (
                <tr key={i}>
                  <td>
                    {configuration.name}
                  </td>
                  <td>
                    {configuration.description}
                  </td>
                  <td>
                    <Button
                      bsSize="small"
                      onClick={() => this.onClick(configuration.yaml)}
                    >
                      Load YAML
                    </Button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </Table>
      </div>
    );
  }
}

const StoredConfContainer = connect(
  state => {
    return {
      configurations: state.configurations
    };
  },
  dispatch => {
    return {
      getConfigurations: url => dispatch(getConfigurations(url)),
      setYaml: yaml => dispatch(change("ExportForm", "feature_selection", yaml))
    };
  }
)(StoredConfComponent);

const SelectFeatures = ({
  next,
  onDrop,
  featuresUi,
  switchToTreeTag,
  setYaml,
  switchToYaml,
  switchToStoredConf,
  onSearchChange,
  clearSearch,
  onTreeNodeCollapseChange,
  onTreeNodeCheckChange,
  labelFilter,
  tagTreeData
}) =>
  <Row style={{ height: "auto" }}>
    <ButtonGroup justified>
      <Button
        href="#"
        active={featuresUi === "treetag"}
        onClick={switchToTreeTag}
      >
        Tag Tree
      </Button>
      <Button
        href="#"
        active={featuresUi === "stored"}
        onClick={switchToStoredConf}
      >
        Stored Configuration
      </Button>
      <Button href="#" active={featuresUi === "yaml"} onClick={switchToYaml}>
        YAML
      </Button>
    </ButtonGroup>
    {featuresUi === "treetag"
      ? <TreeTagUi
          onSearchChange={onSearchChange}
          clearSearch={clearSearch}
          onTreeNodeCollapseChange={onTreeNodeCollapseChange}
          onTreeNodeCheckChange={onTreeNodeCheckChange}
          labelFilter={labelFilter}
          tagTreeData={tagTreeData}
        />
      : null}
    {featuresUi === "stored"
      ? <StoredConfContainer switchToYaml={switchToYaml} />
      : null}
    {featuresUi === "yaml" ? <YamlUi onDrop={onDrop} /> : null}
    <Button bsSize="large" style={{ float: "right" }} onClick={next}>
      Next
    </Button>
  </Row>;

const ChooseFormats = ({ next }) =>
  <Row>
    <Field
      name="export_formats"
      label="File Formats"
      component={renderCheckboxes}
    >
      {getFormatCheckboxes(AVAILABLE_EXPORT_FORMATS)}
    </Field>
    <Button bsSize="large" style={{ float: "right" }} onClick={next}>
      Next
    </Button>
  </Row>;

const Summary = ({ handleSubmit, formValues, error }) =>
  <Row>
    <Col xs={6}>
      <strong>Name:</strong> {formValues.name}
      <br />
      <strong>Description:</strong> {formValues.description}
      <br />
      <strong>Activation:</strong> {formValues.project}
      <br />
      <strong>Export Formats:</strong>
      <ul>
        {formValues.export_formats &&
          formValues.export_formats.map((format, idx) =>
            <li key={idx}>
              {AVAILABLE_EXPORT_FORMATS[format]}
            </li>
          )}
      </ul>
    </Col>
    <Col xs={6}>
      <Field
        name="buffer_aoi"
        description="Buffer AOI"
        component={renderCheckbox}
        type="checkbox"
      />
      <Field
        name="published"
        description="Publish this export"
        component={renderCheckbox}
        type="checkbox"
      />
      <Button
        bsStyle="success"
        bsSize="large"
        type="submit"
        style={{ width: "100%" }}
        onClick={handleSubmit}
      >
        Create Export
      </Button>
      {error &&
        <p className={styles.error}>
          <strong>
            {error}
          </strong>
        </p>}
    </Col>
  </Row>;

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

  onSearchChange = e => {
    this.setState({
      searchQuery: e.target.value,
      tagTreeData: this.tagTree.visibleData(e.target.value)
    });
  };

  clearSearch = e => {
    this.setState({ searchQuery: "", tagTreeData: this.tagTree.visibleData() });
  };

  describeExport = () => {
    const { dispatch } = this.props;

    dispatch(push("/exports/new/describe"));
  };

  selectFeatures = () => {
    const { dispatch } = this.props;

    dispatch(push("/exports/new/select"));
  };

  chooseFormats = () => {
    const { dispatch } = this.props;

    dispatch(push("/exports/new/formats"));
  };

  showSummary = () => {
    const { dispatch } = this.props;

    dispatch(push("/exports/new/summary"));
  };

  switchToTreeTag = () => {
    const { dispatch } = this.props;

    dispatch(push("/exports/new/select/treetag"));
  };

  switchToYaml = () => {
    const { dispatch } = this.props;

    dispatch(push("/exports/new/select/yaml"));
  };

  switchToStoredConf = () => {
    const { dispatch } = this.props;

    dispatch(push("/exports/new/select/stored"));
  };

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

  setFormGeoJSON = geojson => {
    this.props.change("the_geom", geojson);
  };

  render() {
    const {
      error,
      formValues,
      formValues: { export_formats: exportFormats },
      handleSubmit,
      match: { params: { featuresUi, step } },
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
            <Nav
              bsStyle="tabs"
              activeKey={step}
              style={{ marginBottom: "20px" }}
            >
              <NavItem eventKey="describe" onClick={this.describeExport}>
                {++idx} Describe Export
              </NavItem>
              <NavItem eventKey="formats" onClick={this.chooseFormats}>
                {++idx} Choose Formats
              </NavItem>
              {requiresFeatureSelection &&
                <NavItem eventKey="select" onClick={this.selectFeatures}>
                  {++idx} Select Features
                </NavItem>}
              <NavItem eventKey="summary" onClick={this.showSummary}>
                {++idx} Summary
              </NavItem>
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
                  <Describe next={this.chooseFormats} {...props} />}
              />
              <Route
                path="/exports/new/select"
                exact
                render={props => <Redirect to="/exports/new/select/treetag" />}
              />
              <Route
                path="/exports/new/select/:featuresUi"
                render={props =>
                  <SelectFeatures
                    next={this.showSummary}
                    onDrop={this.onDrop}
                    featuresUi={featuresUi}
                    switchToTreeTag={this.switchToTreeTag}
                    switchToYaml={this.switchToYaml}
                    switchToStoredConf={this.switchToStoredConf}
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
                        ? this.selectFeatures
                        : this.showSummary
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
              OpenStreetMap database last updated {overpassLastUpdated}
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
      "project",
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
  getOverpassTimestamp
})(form(ExportForm));
