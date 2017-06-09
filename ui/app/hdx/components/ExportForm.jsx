import React, {Component} from 'react';
import { Nav, NavItem, ButtonGroup, FormGroup, ControlLabel, FormControl, HelpBlock, Row, Col, Checkbox, Panel, Button, Table } from 'react-bootstrap';
import { Field, SubmissionError, formValueSelector, propTypes, reduxForm } from 'redux-form';
import { connect } from 'react-redux';
import ExportAOI from './ExportAOI';

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

const renderDescribe = <Row>
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
    <Button>Next</Button>
  </Row>

const renderSelectFeatures = (
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
      <Button>Next</Button>
    </Row>
)

const renderChooseFormats = (
    <Row>
      <Field
        name='export_formats'
        label='File Formats'
        component={renderCheckboxes}
      >
        {getFormatCheckboxes()}
      </Field>
      <Button>Next</Button>
    </Row>
)

const renderSummary = (
  <Row>
    <Button>Create Export</Button>
  </Row>
)

const form = reduxForm({
  form: "ExportForm"
})

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
    return( 
      <Row style={{height: '100%'}}>
        <Col xs={6} style={{height: '100%', overflowY: 'scroll'}}>
          <Nav bsStyle="tabs" activeKey={this.state.step.toString()}>
            <NavItem eventKey="1" onClick={this.handleStep1}>1 Describe Export</NavItem>
            <NavItem eventKey="2" onClick={this.handleStep2}>2 Select Features</NavItem>
            <NavItem eventKey="3" onClick={this.handleStep3}>3 Choose Formats</NavItem>
            <NavItem eventKey="4" onClick={this.handleStep4}>4 Summary</NavItem>
          </Nav>
          <form>
            { this.state.step == '1' ? renderDescribe : null }
            { this.state.step == '2' ? renderSelectFeatures : null }
            { this.state.step == '3' ? renderChooseFormats : null }
            { this.state.step == '4' ? renderSummary: null }
          </form>
        </Col>
        <Col xs={6} style={{height: '100%', overflowY: 'scroll'}}>
          <ExportAOI/>
        </Col>
      </Row>)
  }
}

export default connect()(form(ExportForm));
