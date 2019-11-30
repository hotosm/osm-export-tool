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
import { renderSelect } from "./utils";
import moment from "moment";

const form = reduxForm({
  form: "StatsForm"
});

const pointToFeature = b => {
  return {
    "type":"Feature",
    "geometry":{
      "type":"Point",
      "coordinates":[b[0],b[1]]
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
  }

  componentDidMount() {
    return this.props.getStats(this.props.initialValues) 
  }

  fetch = () => {
    return this.props.getStats(this.props.formValues) 
  }

  render() {
    return <Row style={{ height: "100%" }}>
      <Col xs={6} style={{ height: "100%", padding: "20px",'overflowY':'scroll' }}>
        <h1>Stats</h1>
        <InputGroup>
          <InputGroup.Addon>Date Range:</InputGroup.Addon>
          <Fields component={renderDateRange} names={["before", "after"]} />
        </InputGroup>
        <Field
          name="period"
          component={renderSelect}
        >
          <option value="day">By day</option>
          <option value="week">By week</option>
          <option value="month">By month</option>
        </Field>
        <Button
          bsStyle="primary"
          type="submit"
          onClick={this.fetch}
        >
        <FormattedMessage id="ui.search" defaultMessage="Get stats" />
        </Button>
        <Button style={{marginLeft:"16px"}}>Download CSV</Button>
        <Table>
          <thead>
            <tr>
              <th>
                Period
              </th>
              <th>
                # new users
              </th>
              <th>
                # exports
              </th>
              <th>
                Top Regions
              </th>
            </tr>
          </thead>
          <tbody>
          {this.props.periods.map((period, i) =>
            <tr key={i}>
              <td>
                {period.start_date}
              </td>
              <td>
                {period.users_count}
              </td>
              <td>
                {period.jobs_count}
              </td>
              <td>
                {period.top_regions}
              </td>
            </tr>
          )}
        </tbody>
      </Table>
      </Col>
      <Col xs={6} style={{ height: "100%" }}>
        <MapListView features={{features:this.props.geoms.map(point => pointToFeature(point)),"type":"FeatureCollection"}} />
      </Col>
    </Row>;
  }
}

const mapStateToProps = state => {
  return {
    formValues: formValueSelector("StatsForm")(
      state,
      "before",
      "after",
      "period"
    ),
    initialValues: {
      before:moment().toDate(),
      after:moment().subtract(30,'days').toDate(),
      period:'day'
    },
    geoms: state.stats.geoms,
    periods: state.stats.periods
  }
};

export default connect(mapStateToProps,{getStats})(form(Stats));
