import area from "@turf/area";
import React, { Component } from "react";
import {
  Nav,
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
import {
  FormattedNumber,
  FormattedMessage,
  defineMessages,
  injectIntl
} from "react-intl";
import { connect } from "react-redux";
import { Redirect, Route, Switch } from "react-router";
import { Link, NavLink } from "react-router-dom";
import { push } from "react-router-redux";
import {
  Field,
  Fields,
  formValueSelector,
  reduxForm,
  change
} from "redux-form";

import ExportAOIField from "./ExportAOIField";
import FilterForm from "./FilterForm";
import TreeMenu from "./react-tree-menu/TreeMenu";
import Paginator from "./Paginator";
import { getConfigurations } from "../actions/configurations";
import { createExport, getOverpassTimestamp } from "../actions/exports";
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

const messages = defineMessages({
  bufferAOIDescription: {
    id: "export.buffer_aoi.description",
    defaultMessage: "Buffer AOI"
  },
  configurationTitle: {
    id: "configuration.title",
    defaultMessage: "Configurations"
  },
  descriptionLabel: {
    id: "export.description.label",
    defaultMessage: "Description"
  },
  featureSelectionLabel: {
    id: "export.feature_selection.label",
    defaultMessage: "Feature Selection"
  },
  nameLabel: {
    id: "export.name.label",
    defaultMessage: "Name"
  },
  namePlaceholder: {
    id: "export.name.placeholder",
    defaultMessage: "Name this export"
  },
  projectLabel: {
    id: "export.project.label",
    defaultMessage: "Project"
  },
  projectPlaceholder: {
    id: "export.project.placeholder",
    defaultMessage: "Which activation this export is for"
  },
  publishedDescription: {
    id: "export.published.description",
    defaultMessage: "Publish this Export"
  },
  tagTreeSearchPlaceholder: {
    id: "export.tag_tree_search.placeholder",
    defaultMessage: "Search for a feature type..."
  }
});

const Describe = injectIntl(({ intl: { formatMessage }, next }) =>
  <Row>
    <Field
      name="name"
      type="text"
      label={formatMessage(messages.nameLabel)}
      placeholder={formatMessage(messages.namePlaceholder)}
      component={renderInput}
    />
    <Field
      name="description"
      type="text"
      label={formatMessage(messages.descriptionLabel)}
      component={renderTextArea}
      rows="4"
    />
    <Field
      name="project"
      type="text"
      label={formatMessage(messages.projectLabel)}
      placeholder={formatMessage(messages.projectPlaceholder)}
      component={renderInput}
    />
    <Link className="btn btn-lg btn-primary pull-right" to={next}>
      <FormattedMessage id="nav.next" defaultMessage="Next" />
    </Link>
  </Row>
);

const YamlUi = injectIntl(({ intl: { formatMessage }, onDrop }) =>
  <div>
    <Field
      name="feature_selection"
      type="text"
      label={formatMessage(messages.featureSelectionLabel)}
      component={renderTextArea}
      className={styles.featureSelection}
      rows="10"
    />
    <Dropzone className="nullClassName" onDrop={onDrop}>
      <Button>
        <FormattedMessage
          id="export.feature_selection.load_from_josm_preset"
          defaultMessage="Load from JOSM Preset .XML"
        />
      </Button>
    </Dropzone>
  </div>
);

const CheckboxHelp = props => {
  if (!props.name) {
    return <Panel>Hover over a checkbox to see its definition.</Panel>;
  } else {
    return (
      <Panel>
        <strong>{props.name}</strong>
        <br />
        <strong>Geometry types:</strong>{" "}
        {TAGLOOKUP[props.name]["geom_types"].join(", ")}
        <br />
        <strong>Keys:</strong>
        <ul>
          {TAGLOOKUP[props.name]["keys"].map((o, i) => {
            return (
              <li key={i}>
                {o}
              </li>
            );
          })}
        </ul>
        <strong>Where:</strong> {TAGLOOKUP[props.name]["where"]}
      </Panel>
    );
  }
};

class _TreeTagUi extends Component {
  constructor(props) {
    super();
    this.state = { hoveredCheckboxName: null };
  }

  onCheckboxHover = checkboxName => {
    this.setState({ hoveredCheckboxName: checkboxName });
  };

  render() {
    const {
      clearSearch,
      intl: { formatMessage },
      labelFilter,
      onSearchChange,
      onTreeNodeCheckChange,
      onTreeNodeCollapseChange,
      tagTreeData
    } = this.props;

    return (
      <div>
        <InputGroup
          style={{ width: "100%", marginTop: "20px", marginBottom: "10px" }}
        >
          <FormControl
            id="treeTagSearch"
            type="text"
            placeholder={formatMessage(messages.tagTreeSearchPlaceholder)}
            onChange={onSearchChange}
          />
          <InputGroup.Button>
            <Button onClick={clearSearch}>
              <FormattedMessage id="ui.clear" defaultMessage="Clear" />
            </Button>
          </InputGroup.Button>
        </InputGroup>
        <Col xs={6}>
          <TreeMenu
            data={tagTreeData}
            onTreeNodeCollapseChange={onTreeNodeCollapseChange}
            onTreeNodeCheckChange={onTreeNodeCheckChange}
            expandIconClass="fa fa-chevron-right"
            collapseIconClass="fa fa-chevron-down"
            labelFilter={labelFilter}
            onCheckboxHover={this.onCheckboxHover}
          />
        </Col>
        <Col xs={6}>
          <CheckboxHelp name={this.state.hoveredCheckboxName} />
        </Col>
      </div>
    );
  }
}

const TreeTagUi = injectIntl(_TreeTagUi);

class StoredConfComponent extends Component {
  state = {
    filters: {}
  };

  componentWillMount() {
    this.props.getConfigurations();
  }

  onClick = yaml => {
    this.props.setYaml(yaml);
    this.props.switchToYaml();
  };

  search = ({ search, ...values }) => {
    const { getConfigurations } = this.props;
    const { filters } = this.state;

    const newFilters = {
      ...filters,
      ...values,
      search
    };

    this.setState({
      filters: newFilters
    });

    return getConfigurations(newFilters);
  };

  render() {
    const {
      configurations,
      getConfigurations,
      intl: { formatMessage }
    } = this.props;
    const { filters } = this.state;

    if (configurations.total === 0 && filters === {}) {
      // TODO return something better here
      return null;
    }

    return (
      <div>
        <FilterForm
          type={formatMessage(messages.configurationTitle)}
          onSubmit={this.search}
        />
        <Paginator
          collection={configurations}
          getPage={getConfigurations.bind(null, filters)}
        />
        <Table>
          <thead>
            <tr>
              <th>
                <FormattedMessage
                  id="configuration.name.label"
                  defaultMessage="Name"
                />
              </th>
              <th>
                <FormattedMessage
                  id="configuration.description.label"
                  defaultMessage="Description"
                />
              </th>
              <th />
            </tr>
          </thead>
          <tbody>
            {configurations.items.map((configuration, i) => {
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
                      <FormattedMessage
                        id="configuration.load_yaml"
                        defaultMessage="Load YAML"
                      />
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
)(injectIntl(StoredConfComponent));

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
        <FormattedMessage id="ui.exports.tag_tree" defaultMessage="Tag Tree" />
      </Button>
      {/* TODO don't display this if no configurations are available */}
      <Button
        href="#"
        active={featuresUi === "stored"}
        onClick={switchToStoredConf}
      >
        <FormattedMessage
          id="ui.exports.stored_configuration"
          defaultMessage="Stored Configuration"
        />
      </Button>
      <Button href="#" active={featuresUi === "yaml"} onClick={switchToYaml}>
        YAML
      </Button>
    </ButtonGroup>
    <Row>
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
    </Row>
    <Row>
      <Link className="btn btn-lg btn-primary pull-right" to={next}>
        <FormattedMessage id="nav.next" defaultMessage="Next" />
      </Link>
    </Row>
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
    <Link className="btn btn-lg btn-primary pull-right" to={next}>
      <FormattedMessage id="nav.next" defaultMessage="Next" />
    </Link>
  </Row>;

const Summary = injectIntl(
  ({ error, formValues, handleSubmit, intl: { formatMessage } }) =>
    <Row>
      <Col xs={6}>
        <strong>
          <FormattedMessage id="export.name.label" defaultMessage="Name" />:
        </strong>{" "}
        {formValues.name}
        <br />
        <strong>
          <FormattedMessage
            id="export.description.label"
            defaultMessage="Description"
          />:
        </strong>{" "}
        {formValues.description}
        <br />
        <strong>
          <FormattedMessage
            id="export.project.label"
            defaultMessage="Project"
          />:
        </strong>{" "}
        {formValues.project}
        <br />
        <strong>
          <FormattedMessage
            id="export.export_formats.label"
            defaultMessage="Export Formats"
          />:
        </strong>
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
          description={formatMessage(messages.bufferAOIDescription)}
          component={renderCheckbox}
          type="checkbox"
        />
        <Field
          name="published"
          description={formatMessage(messages.publishedDescription)}
          component={renderCheckbox}
          type="checkbox"
        />
        <Button
          bsStyle="danger"
          bsSize="large"
          type="submit"
          style={{ width: "100%" }}
          onClick={handleSubmit}
        >
          <FormattedMessage
            id="ui.exports.create_export"
            defaultMessage="Create Export"
          />
        </Button>
        {error &&
          <p className={styles.error}>
            <strong>
              {error}
            </strong>
          </p>}
      </Col>
    </Row>
);

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
                  <Describe next="/exports/new/formats" {...props} />}
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
                    next="/exports/new/summary"
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
  createExport,
  getOverpassTimestamp
})(form(ExportForm));
