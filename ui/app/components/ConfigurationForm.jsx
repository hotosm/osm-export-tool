import React, { Component } from 'react';
import { Col, Row, Button } from 'react-bootstrap';
import { connect } from 'react-redux';
import { Field, SubmissionError, formValueSelector, propTypes, reduxForm } from 'redux-form';
import { renderInput, renderTextArea, renderCheckbox  } from './utils';
import { createConfiguration } from '../actions/configurationActions';

const form = reduxForm({
  form:'ConfigurationForm',
  onSubmit:(values,dispatch,props) => {
    console.log("Form submitted:", values)
    dispatch(createConfiguration(values,'ConfigurationForm'))
  }
})

export class ConfigurationForm extends Component {

  render () {
    const handleSubmit = null
    const editing = true

    return (
      <Row style={{height: '100%'}}>
        <form>
          <Field
            name="name"
            type="text"
            label="Name"
            placeholder="Health and Sanitation"
            component={renderInput}
          />
          <Field
            name="description"
            type="text"
            label="Description"
            placeholder="Features for Project A in Region B"
            component={renderTextArea}
            rows='4'
          />
        </form>
        <Field
          name='yaml'
          type="text"
          label='Feature Selection'
          component={renderTextArea}
          rows='12'
        />
        <Field
          name="public"
          description="Public - others can see your configuration"
          type="checkbox"
          component={renderCheckbox}
        />
        <Button bsStyle="success" bsSize="large" type="submit" onClick={this.props.handleSubmit}>
          { editing ? 'Update Configuration' : 'Create Configuration' }
        </Button>
        { editing ? 
        <Button bsStyle="danger" bsSize="large" type="submit" style={{float:'right'}} onClick={this.props.handleSubmit}>
          Delete Configuration
        </Button> : null
        }
      </Row>
    );
  }
}

const mapStateToProps = state => {
  return {
    initialValues: {
      public:true
    }
  };
};

const mapDispatchToProps = dispatch => {
  return {};
};

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(form(ConfigurationForm));
