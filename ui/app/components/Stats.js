import axios from "axios";
import React, { Component, PropTypes } from "react";
import { Link } from "react-router-dom";
import MapListView from "./MapListView";
import { Button, FormControl, InputGroup, Row, Col, Table, Panel } from "react-bootstrap";
import FilterForm from "./FilterForm";
import {
  FormattedMessage,
  defineMessages,
  injectIntl
} from "react-intl";
import { connect } from "react-redux";
import { DateRangeInput } from "@blueprintjs/datetime";
import { Field, Fields, propTypes, reduxForm, formValueSelector } from "redux-form";
import { getStats } from "../actions/exports";

const form = reduxForm({
  form: "StatsForm"
});

const bboxToFeature = b => {
  return {
    "type":"Feature",
    "geometry":{
      "type":"Polygon",
      "coordinates":[[
          [b[0],b[1]],
          [b[2],b[1]],
          [b[2],b[3]],
          [b[0],b[3]],
          [b[0],b[1]]
        ]]
    }
  }
}

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

class Stats extends Component {

  constructor(props) {
    super(props)
    this.state = {last_100_geoms: []}
  }

  componentDidMount() {
    this.fetch()
  }

  fetch = () => {
    return this.props.getStats(this.props.formValues) 
  }

  render() {
    return <Row style={{ height: "100%" }}>
      <Col xs={6} style={{ height: "100%", padding: "20px",'overflowY':'scroll' }}>
        <h1>Stats</h1>
        <Button
          bsStyle="primary"
          className="pull-right"
          type="submit"
          onClick={this.fetch}
        >
        <FormattedMessage id="ui.search" defaultMessage="Filter" />
        </Button>
        <InputGroup>
          <InputGroup.Addon>Date Range:</InputGroup.Addon>
          <Fields component={renderDateRange} names={["before", "after"]} />
        </InputGroup>
        <Panel style={{'marginTop':'20px'}}>
          <h4>Exports: {this.props.jobs_count}</h4>
          <p>Top countries: IN (5), US (2) </p>
          <Button>Download CSV</Button>
        </Panel>
        <Table>
          <thead>
            <tr>
              <th>
                Name
              </th>
              <th>
                Foo
              </th>
            </tr>
          </thead>
          <tbody>
          {this.props.jobs.map((job, i) =>
            <tr key={i}>
              <td>
                {job.name}
              </td>
              <td>
                
              </td>
            </tr>
          )}
        </tbody>
      </Table>
      </Col>
      <Col xs={6} style={{ height: "100%" }}>
        <MapListView features={{features:this.props.jobs.map(job => bboxToFeature(job.geom)),"type":"FeatureCollection"}} />
      </Col>
    </Row>;
  }
}

const mapStateToProps = state => {
  return {
    formValues: formValueSelector("StatsForm")(
      state,
      "before",
      "after"
    ),
    initialValues: {
      "before":new Date(),
      "after":new Date()
    },
    jobs: state.stats.jobs
  }
};

export default connect(mapStateToProps,{getStats})(form(Stats));
