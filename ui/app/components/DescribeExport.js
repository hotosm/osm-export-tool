import React from "react";
import { Row } from "react-bootstrap";
import { FormattedMessage, defineMessages, injectIntl } from "react-intl";
import { Link } from "react-router-dom";
import { Field } from "redux-form";

import { renderInput, renderTextArea } from "./utils";

const messages = defineMessages({
  descriptionLabel: {
    id: "export.description.label",
    defaultMessage: "Description"
  },
  nameLabel: {
    id: "export.name.label",
    defaultMessage: "Name"
  },
  namePlaceholder: {
    id: "export.name.placeholder",
    defaultMessage: "Name this export"
  },
  eventLabel: {
    id: "export.event.label",
    defaultMessage: "Project"
  },
  eventPlaceholder: {
    id: "export.event.placeholder",
    defaultMessage: "Which activation this export is for"
  }
});

export default injectIntl(({ intl: { formatMessage }, next }) =>
  <Row>
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
      component={renderTextArea}
      rows="4"
    />
    <Field
      name="event"
      type="text"
      label={formatMessage(messages.eventLabel)}
      placeholder={formatMessage(messages.eventPlaceholder)}
      component={renderInput}
    />
    <Link className="btn btn-primary pull-right" to={next}>
      <FormattedMessage id="nav.next" defaultMessage="Next" />
    </Link>
  </Row>
);
