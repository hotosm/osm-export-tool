import React from "react";
import { FormattedMessage } from "react-intl";
import { Row } from "react-bootstrap";
import { Link } from "react-router-dom";
import { Field } from "redux-form";

import {
  AVAILABLE_EXPORT_FORMATS,
  OMIT_FROM_FORMAT_OPTIONS,
  getFormatCheckboxes,
  renderCheckboxes
} from "./utils";

const EXPORT_FORMATS = Object.keys(AVAILABLE_EXPORT_FORMATS)
  .filter(x => !Object.keys(OMIT_FROM_FORMAT_OPTIONS).includes(x))
  .reduce((obj, k) => {
    obj[k] = AVAILABLE_EXPORT_FORMATS[k];

    return obj;
  }, {});

export default ({ next }) => (
  <Row>
    <Field
      name="export_formats"
      label="File Formats"
      component={renderCheckboxes}
    >
      &nbsp; See{" "}
      <Link to="/learn/export_formats" target="_blank">
        Learn (Export Formats)
      </Link>{" "}
      for details on each file format.
      {getFormatCheckboxes(EXPORT_FORMATS)}
    </Field>
    <Link className="btn btn-primary pull-right" to={next}>
      <FormattedMessage id="nav.next" defaultMessage="Next" />
    </Link>
  </Row>
);
