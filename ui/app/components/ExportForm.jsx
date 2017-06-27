import React, {Component} from 'react';
import { Nav, NavItem, InputGroup, ButtonGroup, Row, Col, Panel, Button, FormControl, FormGroup, Radio, Table } from 'react-bootstrap';
import { Field, SubmissionError, formValueSelector, propTypes, reduxForm, change } from 'redux-form';
import { connect } from 'react-redux';
import ExportAOI from './aoi/ExportAOI';
import { createExport, getOverpassTimestamp } from '../actions/exportsActions';
import styles from '../styles/ExportForm.css';
import { AVAILABLE_EXPORT_FORMATS, getFormatCheckboxes, renderCheckboxes, renderCheckbox, renderInput, renderTextArea, PresetParser } from './utils';
const Dropzone = require('react-dropzone');
import TreeMenu from './react-tree-menu/TreeMenu'
import { TreeTag, TreeTagYAML } from '../utils/TreeTag'
import { TAGTREE, TAGLOOKUP } from '../utils/TreeTagSettings'
import { getConfigurations, setYaml } from '../actions/configurationActions'

const form = reduxForm({
  form: "ExportForm",
  onSubmit: (values, dispatch, props) => {
    console.log("Submitting form. Values:", values)

    let geom = props.aoiInfo.geojson;
    if (props.aoiInfo.geomType == null) {
      throw new SubmissionError({
        _error: 'Please select an area of interest →'
      });
    }

    if (props.aoiInfo.geojson.geometry) {
      geom = props.aoiInfo.geojson.geometry;
    }

    if (props.aoiInfo.geojson.features) {
      geom = props.aoiInfo.geojson.features[0].geometry;
    }

    const formData = {
      ...values,
      the_geom: geom
    };
    dispatch(createExport(formData,"ExportForm"))
  }
})

const Describe = ({next}) => 
  <Row>
    <Field
      name='name'
      type="text"
      label='Name'
      placeholder="name this export"
      component={renderInput}
    />
    <Field
      name='description'
      type="text"
      label='Description'
      component={renderTextArea}
      rows='4'
    />
    <Field
      name='project'
      type="text"
      label='Project'
      placeholder="which activation this export is for"
      component={renderInput}
    />
    <Button bsSize="large" style={{float:"right"}} onClick={next}>Next</Button>
  </Row>

const YamlUi = ({onDrop}) => 
  <div>
    <Field
      name='feature_selection'
      type="text"
      label='Feature Selection'
      component={renderTextArea}
      className={styles.featureSelection}
      rows='10'
    />
    <Dropzone className="nullClassName" onDrop={onDrop}>
      <Button>Load from JOSM Preset .XML</Button>
    </Dropzone>
  </div>

class TreeTagUi extends React.Component {
    constructor() {
      super();
    }

    render() {
      return <div>
          <InputGroup style={{width:'100%',marginTop:'20px',marginBottom:'10px'}}>
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
        </div>;
    }
}

class StoredConfComponent extends React.Component {
  componentDidMount() {
    this.props.getConfigurations()
  }

  onClick = (yaml) => {
    this.props.setYaml(yaml)
    this.props.switchToYaml()
  }

  render() {
    return <div>
        <InputGroup style={{width:'100%',marginTop:'20px',marginBottom:'10px'}}>
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
        <Table>
          <thead>
            <tr>
              <th>name</th>
              <th>description</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {this.props.configurations.map((configuration,i) => {
              return <tr key={i}>
                <td>{configuration.name}</td>
                <td>{configuration.description}</td>
                <td><Button bsSize="small" onClick={() => this.onClick(configuration.yaml)}>Load YAML</Button></td>
              </tr>
            })}
          </tbody>
        </Table>
      </div>;
  }
}

const StoredConfContainer = connect(
  state => {
    return {
      configurations:state.configurations
    }
  },
  dispatch => {
    return {
      getConfigurations: () => dispatch(getConfigurations),
      setYaml: (yaml) => dispatch(change("ExportForm","feature_selection",yaml))
    }
  }
)(StoredConfComponent);



const SelectFeatures = ({next, onDrop, featuresUi, switchToTreeTag, setYaml, switchToYaml, switchToStoredConf, onSearchChange,clearSearch,onTreeNodeCollapseChange,onTreeNodeCheckChange,labelFilter,tagTreeData}) =>
  <Row>
    <ButtonGroup justified>
      <Button href="#" active={featuresUi === "treetag"} onClick={switchToTreeTag}>Tag Tree</Button>
      <Button href="#" active={featuresUi === "stored"} onClick={switchToStoredConf}>Stored Configuration</Button>
      <Button href="#" active={featuresUi === "yaml"} onClick={switchToYaml}>YAML</Button>
    </ButtonGroup>
    { featuresUi == "treetag" ? <TreeTagUi
        onSearchChange={onSearchChange}
        clearSearch={clearSearch}
        onTreeNodeCollapseChange={onTreeNodeCollapseChange}
        onTreeNodeCheckChange={onTreeNodeCheckChange}
        labelFilter={labelFilter}
        tagTreeData={tagTreeData}
        /> : null }
    { featuresUi == "stored" ? <StoredConfContainer switchToYaml={switchToYaml}/> : null }
    { featuresUi == "yaml" ? <YamlUi onDrop={onDrop}/> : null }
    <Button bsSize="large" style={{float:"right"}} onClick={next}>Next</Button>
  </Row>

const ChooseFormats = ({next}) => 
  <Row>
    <Field
      name='export_formats'
      label='File Formats'
      component={renderCheckboxes}
    >
      {getFormatCheckboxes(AVAILABLE_EXPORT_FORMATS)}
    </Field>
    <Button bsSize="large" style={{float:"right"}} onClick={next}>Next</Button>
  </Row>

const Summary = ({ handleSubmit, formValues, error}) => 
  <Row>
    <Col xs={6}>
      Debugging form values:
      {JSON.stringify(formValues)}
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
      <Button bsStyle="success" bsSize="large" type="submit" style={{width:"100%"}} onClick={handleSubmit}>Create Export</Button>
      {error && <p className={styles.error}><strong>{error}</strong></p>}
    </Col>
  </Row>

export class ExportForm extends Component {
  constructor(props) {
      super(props);
      this.tagTree = new TreeTag(TAGTREE)
      this.state = { step: 1, featuresUi: "treetag", tagTreeData: this.tagTree.visibleData(), searchQuery:"" }
  }

  componentDidMount() {
    this.props.getOverpassTimestamp()
  }

  onTreeNodeCollapseChange = (node) => {
    this.tagTree.onTreeNodeCollapseChange(node)
    this.setState({tagTreeData:this.tagTree.visibleData(this.state.searchQuery)})
  }

  onTreeNodeCheckChange = (node) => {
    this.tagTree.onTreeNodeCheckChange(node)
    const y = new TreeTagYAML(TAGLOOKUP,this.tagTree.checkedValues())
    this.props.change("feature_selection",y.dataAsYaml())
    this.setState({tagTreeData:this.tagTree.visibleData(this.state.searchQuery)})
  }

  onSearchChange = (e) => {
    this.setState({searchQuery:e.target.value,tagTreeData:this.tagTree.visibleData(e.target.value)})
  } 

  clearSearch = (e) => {
    this.setState({searchQuery:'',tagTreeData:this.tagTree.visibleData()})
  }

  handleStep1 = () => {
    this.setState({step:1})
  }

  handleStep2 = () => {
    this.setState({step:2})
  }

  handleStep3 = () => {
    this.setState({step:3})
  }

  handleStep4 = () => {
    this.setState({step:4})
  }

  switchToTreeTag = () => {
    this.setState({featuresUi:"treetag"})
  }

  switchToYaml= () => {
    this.setState({featuresUi:"yaml"})
  }

  switchToStoredConf = () => {
    this.setState({featuresUi:"stored"})
  }

  onDrop = (files) => {
    const file = files[0]
    const reader = new FileReader();
    reader.onload = () => {
      const data = reader.result;
      const p = new PresetParser(data);
      this.props.change("feature_selection",p.as_yaml())
    }
    reader.readAsText(file)
  }

  render() {
    const { handleSubmit, formValues, error, overpassLastUpdated } = this.props
    return( 
      <Row style={{height: '100%'}}>
        <Col xs={6} style={{height: '100%', overflowY: 'scroll', padding:"20px"}}>
          <Nav bsStyle="tabs" activeKey={this.state.step.toString()} style={{marginBottom:"20px"}}>
            <NavItem eventKey="1" onClick={this.handleStep1}>1 Describe Export</NavItem>
            <NavItem eventKey="2" onClick={this.handleStep2}>2 Select Features</NavItem>
            <NavItem eventKey="3" onClick={this.handleStep3}>3 Choose Formats</NavItem>
            <NavItem eventKey="4" onClick={this.handleStep4}>4 Summary</NavItem>
          </Nav>
          <form>
            { this.state.step == '1' ? <Describe next={this.handleStep2}/> : null }
            { this.state.step == '2' ? <SelectFeatures 
              next={this.handleStep3} 
              onDrop={this.onDrop} 
              featuresUi={this.state.featuresUi}
              switchToTreeTag={this.switchToTreeTag}
              switchToYaml={this.switchToYaml}
              switchToStoredConf ={this.switchToStoredConf}
              tagTreeData={this.state.tagTreeData}
              onSearchChange={this.onSearchChange}
              clearSearch={this.clearSearch}
              onTreeNodeCheckChange={this.onTreeNodeCheckChange}
              onTreeNodeCollapseChange={this.onTreeNodeCollapseChange}
              labelFilter={this.tagTree.labelFilter}
            /> : null }
            { this.state.step == '3' ? <ChooseFormats next={this.handleStep4}/> : null }
            { this.state.step == '4' ? <Summary handleSubmit={handleSubmit} formValues={formValues} error={error}/>: null }
          </form>
          <Panel style={{marginTop:'20px'}}>
            OpenStreetMap database last updated {overpassLastUpdated} 
          </Panel>
        </Col>
        <Col xs={6} style={{height: '100%', overflowY: 'scroll'}}>
          <ExportAOI/>
        </Col>
      </Row>
      )
  }
}

const mapStateToProps = state => {
  return {
    aoiInfo: state.aoiInfo,
    formValues:formValueSelector("ExportForm")(state,"name","description","project"),
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
      export_formats:["shp"]
    }
  }
}

const mapDispatchToProps = dispatch => {
  return {
    getOverpassTimestamp: () => dispatch(getOverpassTimestamp)
  }
}

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(form(ExportForm));
