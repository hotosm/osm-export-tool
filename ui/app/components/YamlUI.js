import React from "react";
import { Button } from "react-bootstrap";
import Dropzone from "react-dropzone";
import { FormattedMessage, defineMessages, injectIntl } from "react-intl";
import { Field } from "redux-form";

import { renderTextArea } from "./utils";
import styles from "../styles/ExportForm.css";

const messages = defineMessages({
  featureSelectionLabel: {
    id: "export.feature_selection.label",
    defaultMessage: "Feature Selection"
  }
});

export default injectIntl(({ intl: { formatMessage }, onDrop }) =>
  <div>
    <Field
      name="feature_selection"
      type="text"
      label={formatMessage(messages.featureSelectionLabel)}
      component={renderTextArea}
      className={styles.featureSelection}
      rows="10"
    />
    <Dropzone className="nullClassName" onDrop={onDrop}>
      <Button>
        <FormattedMessage
          id="export.feature_selection.load_from_josm_preset"
          defaultMessage="Load from JOSM Preset .XML"
        />
      </Button>
    </Dropzone>
  </div>
);
