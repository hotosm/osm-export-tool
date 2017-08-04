import React, { Component } from "react";
import {
  Button,
  ControlLabel,
  FormControl,
  FormGroup,
  InputGroup
} from "react-bootstrap";
import { FormattedMessage, defineMessages, injectIntl } from "react-intl";
import { Field, propTypes, reduxForm } from "redux-form";

import { renderCheckbox } from "./utils";

const form = reduxForm({
  form: "ExportSearchForm"
});

const messages = defineMessages({
  showAll: {
    id: "ui.search.show_all",
    defaultMessage: "Show all {type}"
  },
  searchPlaceholder: {
    id: "ui.search.placeholder",
    defaultMessage: "Name or description"
  }
});

class Input extends Component {
  render() {
    const {
      feedbackIcon,
      input,
      label,
      type,
      meta: { error, warning, touched },
      ...props
    } = this.props;

    let message;
    const validationState =
      (touched && (error && "error")) || (warning && "warning") || null;

    if (touched && (error || warning)) {
      message = (
        <span className="help-block">
          {error || warning}
        </span>
      );
    }

    return (
      <FormGroup validationState={validationState}>
        {label &&
          <ControlLabel>
            {label}
          </ControlLabel>}
        <FormControl {...input} type={type} {...props} />
        {feedbackIcon &&
          <FormControl.Feedback>
            {feedbackIcon}
          </FormControl.Feedback>}
        {message}
      </FormGroup>
    );
  }
}
class ExportSearchForm extends Component {
  static propTypes = {
    ...propTypes
  };

  render() {
    const { handleSubmit, intl: { formatMessage }, running, type } = this.props;

    return (
      <form onSubmit={this.search}>
        <InputGroup
          style={{
            width: "100%",
            marginTop: "20px",
            marginBottom: "10px"
          }}
        >
          <Field
            component={Input}
            componentClass="input"
            name="search"
            placeholder={formatMessage(messages.searchPlaceholder)}
            type="text"
          />
          <InputGroup.Button>
            <Button
              bsStyle="primary"
              disabled={running}
              type="submit"
              onClick={handleSubmit}
            >
              <FormattedMessage id="ui.search" defaultMessage="Search" />
            </Button>
          </InputGroup.Button>
        </InputGroup>
        <Field
          component={renderCheckbox}
          description={formatMessage(messages.showAll, {
            type
          })}
          name="all"
          style={{ paddingLeft: 12 }}
          type="checkbox"
        />
      </form>
    );
  }
}

export default form(injectIntl(ExportSearchForm));
