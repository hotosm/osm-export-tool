import React, {Component} from 'react';
import { Nav, NavItem, ButtonGroup, FormGroup, ControlLabel, FormControl, HelpBlock, Row, Col, Checkbox, Panel, Button, Table } from 'react-bootstrap';
import { Field, SubmissionError, formValueSelector, propTypes, reduxForm } from 'redux-form';
import { connect } from 'react-redux';
import ExportAOI from './ExportAOI';

const AVAILABLE_EXPORT_FORMATS = {
  shp: 'ESRI Shapefiles',
  geopackage: 'GeoPackage',
  garmin_img: 'Garmin .IMG',
  kml: '.KMZ'
};

const getFormatCheckboxes = () =>
  Object.keys(AVAILABLE_EXPORT_FORMATS).map((k, i) =>
    <Field
      key={i}
      name={k}
      description={AVAILABLE_EXPORT_FORMATS[k]}
      component={renderCheckbox}
      type='checkbox'
    />);

const renderCheckboxes = ({id, label, input, data, meta: { error }, description, ...props}) =>
  <FormGroup controlId={id || input.name} validationState={error && 'error'}>
    <ControlLabel>{label}</ControlLabel>
    {props.children}
    <FormControl.Feedback />
    <HelpBlock>{error && <span className={styles.error}>{error}</span>}</HelpBlock>
  </FormGroup>;

const renderCheckbox = ({input, data, description, meta, ...props}) =>
  <Checkbox {...input} {...props}>{description}</Checkbox>;

const renderDescribe = <Row></Row>

const renderSelectFeatures = (
    <ButtonGroup justified>
      <Button href="#">Tree Tag</Button>
      <Button href="#">YAML</Button>
    </ButtonGroup>)

const renderChooseFormats = (
    <Field
      name='export_formats'
      label='File Formats'
      component={renderCheckboxes}
    >
      {getFormatCheckboxes()}
    </Field>

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

  render() {
    return( 
      <Row style={{height: '100%'}}>
        <Col xs={6} style={{height: '100%', overflowY: 'scroll'}}>
          <Nav bsStyle="tabs" activeKey={this.state.step.toString()}>
            <NavItem eventKey="1" onClick={this.handleStep1}>1 Describe Export</NavItem>
            <NavItem eventKey="2" onClick={this.handleStep2}>2 Select Features</NavItem>
            <NavItem eventKey="3" onClick={this.handleStep3}>3 Choose Formats</NavItem>
          </Nav>
          <form>
            { this.state.step == '1' ? renderDescribe : null }
            { this.state.step == '2' ? renderSelectFeatures : null }
            { this.state.step == '3' ? renderChooseFormats : null }
          </form>
        </Col>
        <Col xs={6} style={{height: '100%', overflowY: 'scroll'}}>
          <ExportAOI/>
        </Col>
      </Row>)
  }
}

export default connect()(form(ExportForm));
