import React, { Component } from "react";
import { Row, Button } from "react-bootstrap";
import { FormattedMessage, defineMessages, injectIntl } from "react-intl";
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

const messages = defineMessages({
  descriptionLabel: {
    id: "configuration.description.label",
    defaultMessage: "Description"
  },
  descriptionPlaceholder: {
    id: "configuration.description.placeholder",
    defaultMessage: "Features for Project A in Region B"
  },
  featureSelectionLabel: {
    id: "configuration.feature_selection.label",
    defaultMessage: "Feature Selection"
  },
  nameLabel: {
    id: "configuration.name.label",
    defaultMessage: "Name"
  },
  namePlaceholder: {
    id: "configuration.name.placeholder",
    defaultMessage: "Health and Sanitation"
  },
  publicDescription: {
    id: "configuration.public.description",
    defaultMessage: "Publish this Configuration"
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
    const { intl: { formatMessage } } = this.props;
    const editing = this.props.configurationUid != null;

    return (
      <Row style={{ height: "100%" }}>
        <form>
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
            placeholder={formatMessage(messages.descriptionPlaceholder)}
            component={renderTextArea}
            rows="4"
          />
        </form>
        <Field
          name="yaml"
          type="text"
          label={formatMessage((messages.featureSelectionLabel))}
          component={renderTextArea}
          rows="12"
          className={styles.featureSelection}
        />
        <Field
          name="public"
          description={formatMessage(messages.publicDescription)}
          type="checkbox"
          component={renderCheckbox}
        />
        <Button
          bsStyle="primary"
          bsSize="large"
          type="submit"
          onClick={this.props.handleSubmit}
        >
          {editing
            ? <FormattedMessage
                id="ui.configuration.update"
                defaultMessage="Update Configuration"
              />
            : <FormattedMessage
                id="ui.configuration.create"
                defaultMessage="Create Configuration"
              />}
        </Button>
        {editing
          ? <Button
              bsStyle="danger"
              bsSize="large"
              type="submit"
              style={{ float: "right" }}
              onClick={this.handleDelete}
            >
              <FormattedMessage
                id="ui.configuration.delete"
                defaultMessage="Delete Configuration"
              />
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

export default connect(mapStateToProps, { handleDelete: deleteConfiguration })(
  form(injectIntl(ConfigurationForm))
);
