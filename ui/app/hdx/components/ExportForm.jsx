import React, {Component} from 'react';
import { Nav, NavItem, ButtonGroup, FormGroup, ControlLabel, FormControl, HelpBlock, Row, Col, Checkbox, Panel, Button, Table } from 'react-bootstrap';
import { Field, SubmissionError, formValueSelector, propTypes, reduxForm } from 'redux-form';
import { connect } from 'react-redux';
import ExportAOI from './ExportAOI';
import { createExport } from '../actions/exportsActions';
import styles from '../styles/ExportForm.css';

const AVAILABLE_EXPORT_FORMATS = {
  shp: 'ESRI Shapefiles',
  geopackage: 'GeoPackage',
  garmin_img: 'Garmin .IMG',
  kml: 'Google Earth .KMZ',
  xml: 'OSM .XML',
  pbf: 'OSM .PBF'
};

const getFormatCheckboxes = () =>
    <Field
      name="export_formats"
      component={(props) => {
        const ks = Object.keys(AVAILABLE_EXPORT_FORMATS).map((k, i) =>
          <Checkbox
          key={i}
          name={k}
          checked={props.input.value.indexOf(k) !== -1}
          onChange={event => {
            const newValue = [...props.input.value];
            if(event.target.checked) {
              newValue.push(k);
            } else {
              newValue.splice(newValue.indexOf(k), 1);
            }
            return props.input.onChange(newValue);
          }}>
          {AVAILABLE_EXPORT_FORMATS[k]}
          </Checkbox>
        );
        return <div>{ks}</div>
      }}/>

const renderCheckboxes = ({id, label, input, data, meta: { error }, description, ...props}) =>
  <FormGroup controlId={id || input.name} validationState={error && 'error'}>
    <ControlLabel>{label}</ControlLabel>
    {props.children}
    <FormControl.Feedback />
    <HelpBlock>{error && <span className={styles.error}>{error}</span>}</HelpBlock>
  </FormGroup>;

const renderCheckbox = ({input, data, description, meta, ...props}) =>
  <Checkbox {...input} {...props}>{description}</Checkbox>;

const renderInput = ({ id, input, label, help, meta: { error }, ...props }) =>
  <FormGroup controlId={id || props.name} validationState={error && 'error'}>
    <ControlLabel>{label}</ControlLabel>
    <FormControl {...input} {...props} />
    <FormControl.Feedback />
    <HelpBlock>{error && <p className={styles.error}>{error}</p>}{help}</HelpBlock>
  </FormGroup>;

const renderTextArea = ({id, label, input, data, meta: { error }, ...props}) =>
  <FormGroup controlId={id || input.name} validationState={error && 'error'}>
    <ControlLabel>{label}</ControlLabel>
    <FormControl componentClass='textarea' {...input} {...props} />
    <FormControl.Feedback />
    <HelpBlock>{error && <span className={styles.error}>{error}</span>}</HelpBlock>
  </FormGroup>;



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
  },

  validate: values => {
    console.log("Validating: ", values)
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
    Coordinates:
    <Button bsSize="large" style={{float:"right"}} onClick={next}>Next</Button>
  </Row>

const SelectFeatures = ({next}) =>
  <Row>
    <ButtonGroup justified>
      <Button href="#">Tree Tag</Button>
      <Button href="#" active={true}>YAML</Button>
    </ButtonGroup>
    <Field
      name='feature_selection'
      type="text"
      label='Feature Selection'
      component={renderTextArea}
      rows='10'
    />
    <Button bsSize="large" style={{float:"right"}} onClick={next}>Next</Button>
  </Row>

const ChooseFormats = ({next}) => 
  <Row>
    <Field
      name='export_formats'
      label='File Formats'
      component={renderCheckboxes}
    >
      {getFormatCheckboxes()}
    </Field>
    <Button bsSize="large" style={{float:"right"}} onClick={next}>Next</Button>
  </Row>

const Summary = ({ handleSubmit, formValues, error}) => 
  <Row>
    <Col xs={6}>
      Summary:
      {JSON.stringify(formValues)}
    </Col>
    <Col xs={6}>
      <Button bsStyle="success" bsSize="large" type="submit" style={{width:"100%"}} onClick={handleSubmit}>Create Export</Button>
      {error && <p className={styles.error}><strong>{error}</strong></p>}
    </Col>
  </Row>

export class ExportForm extends Component {
  constructor(props) {
      super(props);
  }

  state = {
    step: 1
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

  render() {
    const { handleSubmit, formValues, error } = this.props
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
            { this.state.step == '2' ? <SelectFeatures next={this.handleStep3}/> : null }
            { this.state.step == '3' ? <ChooseFormats next={this.handleStep4}/> : null }
            { this.state.step == '4' ? <Summary handleSubmit={handleSubmit} formValues={formValues} error={error}/>: null }
          </form>
        </Col>
        <Col xs={6} style={{height: '100%', overflowY: 'scroll'}}>
          <ExportAOI/>
        </Col>
      </Row>)
  }
}

const mapStateToProps = state => {
  return {
    aoiInfo: state.aoiInfo,
    formValues:formValueSelector("ExportForm")(state,"name","description","project")
  }
}

const mapDispatchToProps = dispatch => {
  return {}
}

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(form(ExportForm));
