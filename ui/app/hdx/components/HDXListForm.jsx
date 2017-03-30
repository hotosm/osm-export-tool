import React, { Component } from 'react';
import { Row, Col, Panel, Button } from 'react-bootstrap';

function DatasetList (props) {
  const listItems = props.datasets.map((dataset) =>
    <li key={dataset}><a target='_blank' href={`https://data.humdata.org/dataset/${dataset}`}>{dataset}</a></li>
  );

  return (
    <ul>
      {listItems}
    </ul>
  );
}

function ExportRegionList (props) {
  const regions = props.regions;
  const listItems = regions.map((region) =>
    <Row key={region.name}>
      <Panel>
        <Col lg={5}>
          <DatasetList datasets={region.datasets} />
        </Col>
        <Col lg={5}>
          Last Run: 2017/03/27 00:00:00PM<br />
          Next Run: none<br />
          Schedule: Every Sunday at 1:00 UTC
        </Col>
        <Col lg={1} md={2}>
          <Button block>
            Map
          </Button>
        </Col>
        <Col lg={1} md={2}>
          <Button block href='edit'>
            Settings
          </Button>
        </Col>
      </Panel>
    </Row>
  );

  return (
    <div>
      {listItems}
    </div>
  );
}

export class HDXListForm extends Component {
  render () {
    const regions = [
      {
        name: 'hotosm_sen',
        datasets: ['hotosm_sen_roads', 'hotosm_sen_buildings', 'hotosm_sen_admin_boundaries', 'hotosm_waterways', 'hotosm_points_of_interest']
      },
      {
        name: 'hotosm_sle',
        datasets: ['hotosm_sle_roads', 'hotosm_sle_buildings']
      },
      {
        name: 'hotosm_mli',
        datasets: ['hotosm_mli_roads', 'hotosm_mli_buildings']
      },
      {
        name: 'hotosm_lbr',
        datasets: ['hotosm_lbr_roads', 'hotosm_lbr_buildings']
      },
      {
        name: 'hotosm_gin',
        datasets: ['hotosm_lbr_roads', 'hotosm_lbr_buildings']
      }
    ];

    return (
      <div style={{padding: '20px'}}>
        <h2 style={{display: 'inline'}}>HDX Export Regions</h2>
        <Button style={{float: 'right'}} bsStyle='primary' bsSize='large' href='create'>
          Create New Export Region
        </Button>
        <hr />
        <ExportRegionList regions={regions} />
      </div>
    );
  }
}

export default HDXListForm;
