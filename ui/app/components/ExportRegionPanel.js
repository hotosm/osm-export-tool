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

import { prettyBytes } from "./utils";
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
}

class ExportRegionPanel extends Component {
  getLastRun() {
    const { region } = this.props;

    if (region.last_run == null) {
      return <FormattedMessage id="ui.never" defaultMessage="Never" />;
    }

    return <FormattedRelative value={region.last_run} />;
  }

  getNextRun() {
    const { region } = this.props;

    if (region.next_run == null) {
      return <FormattedMessage id="ui.never" defaultMessage="Never" />;
    }

    return <FormattedRelative value={region.next_run} />;
  }

  getSchedule() {
    const { region } = this.props;

    const scheduleHour = `0${region.schedule_hour}`.slice(-2);

    switch (region.schedule_period) {
      case "6hrs":
        return (
          <FormattedMessage
            id="exports.schedule.6hrs"
            defaultMessage="Every 6 hours starting at {time} UTC"
            values={{ time: `${scheduleHour}:00` }}
          />
        );

      case "daily":
        return (
          <FormattedMessage
            id="exports.schedule.daily"
            defaultMessage="Every day at {time} UTC"
            values={{ time: `${scheduleHour}:00` }}
          />
        );

      case "weekly":
        return (
          <FormattedMessage
            id="exports.schedule.weekly"
            defaultMessage="Every Sunday at {time} UTC"
            values={{ time: `${scheduleHour}:00` }}
          />
        );

      case "monthly":
        return (
          <FormattedMessage
            id="exports.schedule.monthly"
            defaultMessage="The 1st of every month at {time} UTC"
            values={{ time: `${scheduleHour}:00` }}
          />
        );

      case "disabled":
        return <FormattedMessage id="ui.never" defaultMessage="Never" />;

      default:
        return <FormattedMessage id="ui.unknown" defaultMessage="Unknown" />;
    }
  }

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
          <FormattedMessage
            id="runs.last_run.label"
            defaultMessage="Last Run:"
          />{" "}
          <strong>{this.getLastRun(region)}</strong>
          <br />
          <FormattedMessage
            id="runs.next_run.label"
            defaultMessage="Next Run:"
          />{" "}
          <strong>{this.getNextRun(region)}</strong>
          <br />
          <FormattedMessage
            id="runs.schedule.label"
            defaultMessage="Schedule:"
          />{" "}
          <strong>{this.getSchedule(region)}</strong>
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
