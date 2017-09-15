import React from "react";
import { FormattedMessage } from "react-intl";
import { Row } from "react-bootstrap";
import { Link } from "react-router-dom";
import { Field } from "redux-form";

import {
  AVAILABLE_EXPORT_FORMATS,
  getFormatCheckboxes,
  renderCheckboxes
} from "./utils";

export default ({ next }) =>
  <Row>
    <Field
      name="export_formats"
      label="File Formats"
      component={renderCheckboxes}
    >
       &nbsp; See <Link to="/learn/export_formats" target="_blank">Learn (Export Formats)</Link> for details on each file format.
      {getFormatCheckboxes(AVAILABLE_EXPORT_FORMATS)}
    </Field>
    <Link className="btn btn-primary pull-right" to={next}>
      <FormattedMessage id="nav.next" defaultMessage="Next" />
    </Link>
  </Row>;
