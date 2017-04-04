import React, { Component } from 'react';

import { FormattedRelative, IntlMixin } from 'react-intl';
import { Row, Col, Panel, Button } from 'react-bootstrap';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';

import { getExportRegions } from '../actions/hdxActions';

function DatasetList (props) {
  const listItems = props.datasets.map((dataset, i) =>
    <li key={i}><a target='_blank' href={`https://data.humdata.org/dataset/${dataset}`}>{dataset}</a></li>
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
        <pre>{JSON.stringify(region)}</pre>
        <Col lg={5}>
          <h4><Link to={`/edit/${region.id}`}>{region.name || 'Untitled'}</Link></h4>
          <DatasetList datasets={region.datasets} />
        </Col>
        <Col lg={5}>
          Last Run: {this.getLastRun(region)}<br />
          Next Run: {this.getNextRun(region)}<br />
          Schedule: {this.getSchedule(region)}
        </Col>
        <Col lg={1} md={2}>
          <Button block title='Map'>
            {/* TODO where does this go? */}
            <i className='fa fa-globe' />
          </Button>
        </Col>
        <Col lg={1} md={2}>
          <Link className='btn btn-default btn-block' to={`/edit/${region.id}`} title='Settings'>
            <i className='fa fa-cog' />
          </Link>
        </Col>
      </Panel>
    )
  }
}

class ExportRegionList extends Component {
  render () {
    const { regions } = this.props;

    const listItems = regions.map((region, i) => {
      region.datasets = [
        `${region.dataset_prefix}_admin_boundaries`,
        `${region.dataset_prefix}_buildings`,
        `${region.dataset_prefix}_points_of_interest`,
        `${region.dataset_prefix}_roads`,
        `${region.dataset_prefix}_waterways`
      ];

      return (
        <Row key={i}>
          <ExportRegionPanel region={region} />
        </Row>
      );
    });

    return (
      <div>
        {listItems}
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
        <hr />
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
