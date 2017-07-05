import React, { Component } from 'react';
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
} from 'react-bootstrap';
import { Field, formValueSelector, reduxForm, change } from 'redux-form';
import { connect } from 'react-redux';
import { Redirect, Route, Switch } from 'react-router';
import { push } from 'react-router-redux';
import ExportAOI from './aoi/ExportAOI';
import { createExport, getOverpassTimestamp } from '../actions/exportsActions';
import styles from '../styles/ExportForm.css';
import {
  AVAILABLE_EXPORT_FORMATS,
  getFormatCheckboxes,
  renderCheckboxes,
  renderCheckbox,
  renderInput,
  renderTextArea,
  PresetParser,
  Paginator
} from './utils';
import Dropzone from 'react-dropzone';
import TreeMenu from './react-tree-menu/TreeMenu';
import { TreeTag, TreeTagYAML } from '../utils/TreeTag';
import { TAGTREE, TAGLOOKUP } from '../utils/TreeTagSettings';
import { getConfigurations } from '../actions/configurationActions';

const form = reduxForm({
  form: 'ExportForm',
  onSubmit: (values, dispatch, props) => {
    console.log('Submitting form. Values:', values);
    dispatch(createExport(values, 'ExportForm'));
  }
});

const Describe = ({ next }) =>
  <Row>
    <Field
      name='name'
      type='text'
      label='Name'
      placeholder='name this export'
      component={renderInput}
    />
    <Field
      name='description'
      type='text'
      label='Description'
      component={renderTextArea}
      rows='4'
    />
    <Field
      name='project'
      type='text'
      label='Project'
      placeholder='which activation this export is for'
      component={renderInput}
    />
    <Button bsSize='large' style={{ float: 'right' }} onClick={next}>
      Next
    </Button>
  </Row>;

const YamlUi = ({ onDrop }) =>
  <div>
    <Field
      name='feature_selection'
      type='text'
      label='Feature Selection'
      component={renderTextArea}
      className={styles.featureSelection}
      rows='10'
    />
    <Dropzone className='nullClassName' onDrop={onDrop}>
      <Button>Load from JOSM Preset .XML</Button>
    </Dropzone>
  </div>;

class TreeTagUi extends React.Component {
  render () {
    return (
      <div>
        <InputGroup
          style={{ width: '100%', marginTop: '20px', marginBottom: '10px' }}
        >
          <FormControl
            id='treeTagSearch'
            type='text'
            label='treeTagSearch'
            placeholder='Search for a feature type...'
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
          expandIconClass='fa fa-chevron-right'
          collapseIconClass='fa fa-chevron-down'
          labelFilter={this.props.labelFilter}
        />
      </div>
    );
  }
}

class StoredConfComponent extends React.Component {
  componentDidMount () {
    this.props.getConfigurations();
  }

  onClick = yaml => {
    this.props.setYaml(yaml);
    this.props.switchToYaml();
  };

  render () {
    return (
      <div>
        <InputGroup
          style={{ width: '100%', marginTop: '20px', marginBottom: '10px' }}
        >
          <FormControl
            id='storedConfigSearch'
            type='text'
            label='storedConfigSearch'
            placeholder='Search for a configuration...'
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
                      bsSize='small'
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
      setYaml: yaml => dispatch(change('ExportForm', 'feature_selection', yaml))
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
  <Row style={{ height: 'auto' }}>
    <ButtonGroup justified>
      <Button
        href='#'
        active={featuresUi === 'treetag'}
        onClick={switchToTreeTag}
      >
        Tag Tree
      </Button>
      <Button
        href='#'
        active={featuresUi === 'stored'}
        onClick={switchToStoredConf}
      >
        Stored Configuration
      </Button>
      <Button href='#' active={featuresUi === 'yaml'} onClick={switchToYaml}>
        YAML
      </Button>
    </ButtonGroup>
    {featuresUi === 'treetag'
      ? <TreeTagUi
        onSearchChange={onSearchChange}
        clearSearch={clearSearch}
        onTreeNodeCollapseChange={onTreeNodeCollapseChange}
        onTreeNodeCheckChange={onTreeNodeCheckChange}
        labelFilter={labelFilter}
        tagTreeData={tagTreeData}
      />
      : null}
    {featuresUi === 'stored'
      ? <StoredConfContainer switchToYaml={switchToYaml} />
      : null}
    {featuresUi === 'yaml' ? <YamlUi onDrop={onDrop} /> : null}
    <Button bsSize='large' style={{ float: 'right' }} onClick={next}>
      Next
    </Button>
  </Row>;

const ChooseFormats = ({ next }) =>
  <Row>
    <Field
      name='export_formats'
      label='File Formats'
      component={renderCheckboxes}
    >
      {getFormatCheckboxes(AVAILABLE_EXPORT_FORMATS)}
    </Field>
    <Button bsSize='large' style={{ float: 'right' }} onClick={next}>
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
        name='buffer_aoi'
        description='Buffer AOI'
        component={renderCheckbox}
        type='checkbox'
      />
      <Field
        name='published'
        description='Publish this export'
        component={renderCheckbox}
        type='checkbox'
      />
      <Button
        bsStyle='success'
        bsSize='large'
        type='submit'
        style={{ width: '100%' }}
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

const renderExportAOI = ({ input, meta, ...props }) => {
  return (
    <ExportAOI errors={meta.error} setFormGeoJSON={props.setFormGeoJSON} />
  );
};

export class ExportForm extends Component {
  constructor (props) {
    super(props);
    this.tagTree = new TreeTag(TAGTREE);
    this.state = {
      step: 1,
      featuresUi: 'treetag',
      tagTreeData: this.tagTree.visibleData(),
      searchQuery: ''
    };
  }

  componentDidMount () {
    this.props.getOverpassTimestamp();
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
    this.props.change('feature_selection', y.dataAsYaml());
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
    this.setState({ searchQuery: '', tagTreeData: this.tagTree.visibleData() });
  };

  handleStep1 = () => {
    const { dispatch } = this.props;

    dispatch(push('/exports/new/describe'));
  };

  handleStep2 = () => {
    const { dispatch } = this.props;

    dispatch(push('/exports/new/select'));
  };

  handleStep3 = () => {
    const { dispatch } = this.props;

    dispatch(push('/exports/new/formats'));
  };

  handleStep4 = () => {
    const { dispatch } = this.props;

    dispatch(push('/exports/new/summary'));
  };

  switchToTreeTag = () => {
    this.setState({ featuresUi: 'treetag' });
  };

  switchToYaml = () => {
    this.setState({ featuresUi: 'yaml' });
  };

  switchToStoredConf = () => {
    this.setState({ featuresUi: 'stored' });
  };

  onDrop = files => {
    const file = files[0];
    const reader = new FileReader();
    reader.onload = () => {
      const data = reader.result;
      const p = new PresetParser(data);
      this.props.change('feature_selection', p.as_yaml());
    };
    reader.readAsText(file);
  };

  setFormGeoJSON = geojson => {
    this.props.change('the_geom', geojson);
  };

  render () {
    const {
      error,
      formValues,
      handleSubmit,
      match: { params: { step } },
      overpassLastUpdated
    } = this.props;

    return (
      <Row style={{ height: '100%' }}>
        <form style={{ height: '100%' }}>
          <Col
            xs={6}
            style={{ height: '100%', overflowY: 'scroll', padding: '20px' }}
          >
            <Nav
              bsStyle='tabs'
              activeKey={step}
              style={{ marginBottom: '20px' }}
            >
              <NavItem eventKey='describe' onClick={this.handleStep1}>
                1 Describe Export
              </NavItem>
              <NavItem eventKey='select' onClick={this.handleStep2}>
                2 Select Features
              </NavItem>
              <NavItem eventKey='formats' onClick={this.handleStep3}>
                3 Choose Formats
              </NavItem>
              <NavItem eventKey='summary' onClick={this.handleStep4}>
                4 Summary
              </NavItem>
            </Nav>
            <Switch>
              <Route
                path='/exports/new'
                exact
                render={props => <Redirect to='/exports/new/describe' />}
              />
              <Route
                path='/exports/new/describe'
                render={props =>
                  <Describe next={this.handleStep1} {...props} />}
              />
              <Route
                path='/exports/new/select'
                render={props =>
                  <SelectFeatures
                    next={this.handleStep3}
                    onDrop={this.onDrop}
                    featuresUi={this.state.featuresUi}
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
                path='/exports/new/formats'
                render={props => <ChooseFormats next={this.handleStep4} />}
              />
              <Route
                path='/exports/new/summary'
                render={props =>
                  <Summary
                    handleSubmit={handleSubmit}
                    formValues={formValues}
                    error={error}
                  />}
              />
            </Switch>
            <Panel style={{ marginTop: '20px' }}>
              OpenStreetMap database last updated {overpassLastUpdated}
            </Panel>
          </Col>
          <Col xs={6} style={{ height: '100%', overflowY: 'scroll' }}>
            <Field
              name='the_geom'
              component={renderExportAOI}
              setFormGeoJSON={this.setFormGeoJSON}
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
    formValues: formValueSelector('ExportForm')(
      state,
      'name',
      'description',
      'project',
      'export_formats'
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
      export_formats: ['shp']
    }
  };
};

const mapDispatchToProps = dispatch => {
  return {
    getOverpassTimestamp: () => dispatch(getOverpassTimestamp)
  };
};

export default connect(mapStateToProps, mapDispatchToProps)(form(ExportForm));
