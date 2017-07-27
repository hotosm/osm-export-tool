import React, { Component } from "react";
import { Row, Button } from "react-bootstrap";
import { connect } from "react-redux";
import { Field, propTypes, reduxForm } from "redux-form";

import {
  createConfiguration,
  updateConfiguration,
  deleteConfiguration
} from "../actions/configurations";
import styles from "../styles/ConfigurationForm.css";
import { renderInput, renderTextArea, renderCheckbox } from "./utils";

const FORM_NAME = "ConfigurationForm";

const form = reduxForm({
  form: FORM_NAME,
  onSubmit: (values, dispatch, props) => {
    if (props.configurationUid) {
      dispatch(updateConfiguration(props.configurationUid, values, FORM_NAME));
    } else {
      dispatch(createConfiguration(values, FORM_NAME));
    }
  }
});

export class ConfigurationForm extends Component {
  static propTypes = {
    ...propTypes
  };

  handleDelete = () => {
    this.props.handleDelete(this.props.configurationUid);
  };

  render() {
    const editing = this.props.configurationUid !== undefined;

    return (
      <Row style={{ height: "100%" }}>
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
            rows="4"
          />
        </form>
        <Field
          name="yaml"
          type="text"
          label="Feature Selection"
          component={renderTextArea}
          rows="12"
          className={styles.featureSelection}
        />
        <Field
          name="public"
          description="Public - others can see your configuration"
          type="checkbox"
          component={renderCheckbox}
        />
        <Button
          bsStyle="success"
          bsSize="large"
          type="submit"
          onClick={this.props.handleSubmit}
        >
          {editing ? "Update Configuration" : "Create Configuration"}
        </Button>
        {editing
          ? <Button
              bsStyle="danger"
              bsSize="large"
              type="submit"
              style={{ float: "right" }}
              onClick={this.handleDelete}
            >
              Delete Configuration
            </Button>
          : null}
      </Row>
    );
  }
}

const mapStateToProps = state => {
  return {
    initialValues: {
      public: true
    }
  };
};

const mapDispatchToProps = dispatch => {
  return {
    handleDelete: uid => dispatch(deleteConfiguration(uid))
  };
};

export default connect(mapStateToProps, mapDispatchToProps)(
  form(ConfigurationForm)
);
