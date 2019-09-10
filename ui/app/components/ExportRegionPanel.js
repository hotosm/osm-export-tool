import React, { Component } from "react";

import { Col, Panel, Button } from "react-bootstrap";
import {
  FormattedMessage,
  FormattedRelative,
  defineMessages,
  injectIntl
} from "react-intl";
import { connect } from "react-redux";
import { Link } from "react-router-dom";

import { prettyBytes, getRegionInfo } from "./utils";
import { zoomToExportRegion } from "../actions/hdx";

const messages = defineMessages({
  settings: {
    id: "ui.settings",
    defaultMessage: "Settings"
  },
  showOnMap: {
    id: "ui.show_on_map",
    defaultMessage: "Show on map"
  }
});

function DatasetList(props) {
  const listItems = props.datasets.map((dataset, i) =>
    <li key={i}>
      <a target="_blank" href={dataset.url}>
        <code>
          {dataset.name}
        </code>
      </a>
    </li>
  );

  return (
    <ul>
      {listItems}
    </ul>
  );
};

class ExportRegionPanel extends Component {

  selectRegion = () => this.props.zoomToExportRegion(this.props.region.id);

  render() {
    const { intl: { formatMessage }, region } = this.props;

    return (
      <Panel>
        <h4>
          <Link to={`/hdx/edit/${region.id}`}>
            {region.name ||
              <FormattedMessage id="ui.untitled" defaultMessage="Untitled" />}
          </Link>
          <Link
            className="btn btn-default pull-right"
            to={`/hdx/edit/${region.id}`}
            title={formatMessage(messages.settings)}
          >
            <i className="fa fa-cog" />
          </Link>
          <Button
            title={formatMessage(messages.showOnMap)}
            className="pull-right"
            onClick={this.selectRegion}
          >
            <i className="fa fa-globe" />
          </Button>
        </h4>
        <Col lg={5}>
          {getRegionInfo(region)}
          {region.last_size &&
            <span>
              <br />Size: <strong>{prettyBytes(region.last_size)}</strong>
            </span>}
          {region.is_private &&
            <span>
              <br />
              <strong>
                <FormattedMessage id="ui.private" defaultMessage="Private" />
              </strong>
            </span>}
        </Col>
        <Col lg={7}>
          <DatasetList datasets={region.datasets} />
        </Col>
      </Panel>
    );
  }
}

export default connect(null, { zoomToExportRegion })(
  injectIntl(ExportRegionPanel)
);
