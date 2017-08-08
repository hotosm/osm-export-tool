import { DateRangeInput } from "@blueprintjs/datetime";
import React, { Component } from "react";
import { Button, FormControl, InputGroup, Row } from "react-bootstrap";
import { FormattedMessage, defineMessages, injectIntl } from "react-intl";
import { Field, Fields, propTypes, reduxForm } from "redux-form";

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
    // TODO this is a specific placeholder
    defaultMessage: "Name, description, event, or username"
  }
});

const renderDateRange = fields =>
  <DateRangeInput
    allowSingleDayRange
    contiguousCalendarMonths={false}
    maxDate={new Date()}
    onChange={([after, before]) => {
      fields.after.input.onChange(after);
      fields.before.input.onChange(before);
    }}
    value={[fields.after.input.value, fields.before.input.value]}
  />;

class Input extends Component {
  render() {
    const { input, type, ...props } = this.props;

    return <FormControl {...input} type={type} {...props} />;
  }
}
class ExportSearchForm extends Component {
  static propTypes = {
    ...propTypes
  };

  render() {
    const {
      handleSubmit,
      intl: { formatMessage },
      running,
      showDateRange,
      type
    } = this.props;

    return (
      <form onSubmit={this.search}>
        <Row>
          <InputGroup
            style={{
              width: "100%",
              marginTop: "20px",
              marginBottom: "10px"
            }}
          >
            <InputGroup.Addon>
              <i className="fa fa-search" />
            </InputGroup.Addon>
            <Field
              component={Input}
              componentClass="input"
              name="search"
              placeholder={formatMessage(messages.searchPlaceholder)}
              type="text"
            />
          </InputGroup>
        </Row>
        {showDateRange &&
          <Row>
            <Button
              bsStyle="primary"
              className="pull-right"
              disabled={running}
              style={{
                marginTop: "10px"
              }}
              type="submit"
              onClick={handleSubmit}
            >
              <FormattedMessage id="ui.search" defaultMessage="Search" />
            </Button>
            <InputGroup
              style={{
                width: "70%",
                marginTop: "10px",
                marginRight: "20px",
                marginBottom: "10px"
              }}
            >
              <InputGroup.Addon>Date Range:</InputGroup.Addon>
              <Fields component={renderDateRange} names={["before", "after"]} />
            </InputGroup>
          </Row>}
        <Row>
          {showDateRange ||
            <Button
              bsStyle="primary"
              className="pull-right"
              disabled={running}
              style={{
                marginTop: "10px"
              }}
              type="submit"
              onClick={handleSubmit}
            >
              <FormattedMessage id="ui.search" defaultMessage="Search" />
            </Button>}
          <Field
            component={renderCheckbox}
            description={formatMessage(messages.showAll, {
              type
            })}
            name="all"
            type="checkbox"
          />
        </Row>
      </form>
    );
  }
}

export default form(injectIntl(ExportSearchForm));
