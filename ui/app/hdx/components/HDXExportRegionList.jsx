import React, { Component } from 'react';

import { FormattedRelative, IntlMixin } from 'react-intl';
import { Row, Col, Panel, Button } from 'react-bootstrap';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';

import { getExportRegions } from '../actions/hdxActions';

function DatasetList (props) {
  const listItems = props.datasets.map((dataset, i) =>
    <li key={i}><a target='_blank' href={`https://data.humdata.org/dataset/${dataset}`}><code>{dataset}</code></a></li>
  );

  return (
    <ul>
      {listItems}
    </ul>
  );
}

class ExportRegionPanel extends Component {
  mixins = [IntlMixin];

  getLastRun () {
    const { region } = this.props;

    if (region.last_run == null) {
      return 'Never';
    }

    return <FormattedRelative value={region.last_run} />;
  }

  getNextRun () {
    const { region } = this.props;

    if (region.next_run == null) {
      return 'Never';
    }

    return <FormattedRelative value={region.next_run} />;
  }

  getSchedule () {
    const { region } = this.props;

    const scheduleHour = `0${region.schedule_hour}`.slice(-2);

    switch (region.schedule_period) {
      case '6hrs':
        return `Every 6 hours starting at ${scheduleHour}:00 UTC`;

      case 'daily':
        return `Every day at ${scheduleHour}:00 UTC`;

      case 'weekly':
        return `Every Sunday at ${scheduleHour}:00 UTC`;

      case 'monthly':
        return `The 1st of every month at ${scheduleHour}:00 UTC`;

      case 'disabled':
        return 'Never';

      default:
        return 'Unknown';
    }
  }

  render () {
    const { region } = this.props;

    return (
      <Panel>
        <h4>
          <Link to={`/edit/${region.id}`}>{region.name || 'Untitled'}</Link>
        </h4>
        <Col lg={5}>
          Last Run: <strong>{this.getLastRun(region)}</strong><br />
          Next Run: <strong>{this.getNextRun(region)}</strong><br />
          Schedule: <strong>{this.getSchedule(region)}</strong>
        </Col>
        <Col lg={7}>
          <DatasetList datasets={region.datasets} />
        </Col>
      </Panel>
    );
  }
}

class ExportRegionList extends Component {
  render () {
    const { regions } = this.props;

    if (regions == null || regions.length === 0) {
      return null;
    }

    return (
      <div>
        <hr />
        {regions.map((region, i) => {
          return (
            <Row key={i}>
              <ExportRegionPanel region={region} />
            </Row>
          );
        })}
      </div>
    );
  }
}

export class HDXExportRegionList extends Component {
  componentDidMount () {
    const { getExportRegions } = this.props;

    getExportRegions();
  }

  render () {
    const { hdx: { exportRegions } } = this.props;

    return (
      <div style={{padding: '20px'}}>
        <h2 style={{display: 'inline'}}>HDX Export Regions</h2>
        <Link to='/new' style={{float: 'right'}} className='btn btn-primary btn-lg'>
          Create New Export Region
        </Link>
        <ExportRegionList regions={exportRegions} />
      </div>
    );
  }
}

const mapStateToProps = state => {
  return {
    hdx: state.hdx
  };
};

const mapDispatchToProps = dispatch => {
  return {
    getExportRegions: () => {
      dispatch(getExportRegions());
    }
  };
};

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(HDXExportRegionList);
