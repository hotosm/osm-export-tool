import axios from "axios";
import React, { Component, PropTypes } from "react";
import { Link } from "react-router-dom";
import { Row, Col, Panel } from "react-bootstrap";
import MapListView from "./MapListView";

export default class Stats extends Component {

  constructor(props) {
    super(props)
    this.state = {last_100_geoms: []}
  }

  componentDidMount() {

    console.log("Fetch stats")

    axios({
      baseURL: window.EXPORTS_API_URL,
      url: "/api/stats"
    })
    .then(rsp => {
      this.setState({
        users_day:rsp.data.new_users[0],
        users_week:rsp.data.new_users[1],
        users_month:rsp.data.new_users[2],
        exports_day:rsp.data.new_exports[0],
        exports_week:rsp.data.new_exports[1],
        exports_month:rsp.data.new_exports[2],
        last_100_geoms: rsp.data.last_100_bboxes.map(b => {
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
        })
      })
    })
  }


  render() {
    return <Row style={{ height: "100%" }}>
      <Col xs={6} style={{ height: "100%", padding: "20px" }}>
        <Panel>
          <h3>New Users</h3>
          <Col sm={4}>
            Past Day
            <h1>{this.state.users_day}</h1>
          </Col>
          <Col sm={4}>
            Past Week
            <h1>{this.state.users_week}</h1>
          </Col>
          <Col sm={4}>
            Past Month
            <h1>{this.state.users_month}</h1>
          </Col>
        </Panel>
        <Panel>
          <h3>Exports Created</h3>
          <Col sm={4}>
            Past Day
            <h1>{this.state.exports_day}</h1>
          </Col>
          <Col sm={4}>
            Past Week
            <h1>{this.state.exports_week}</h1>
          </Col>
          <Col sm={4}>
            Past Month
            <h1>{this.state.exports_month}</h1>
          </Col>
        </Panel>
      </Col>
      <Col xs={6} style={{ height: "100%" }}>
        <MapListView features={{features:this.state.last_100_geoms,"type":"FeatureCollection"}} />
      </Col>
    </Row>;
  }
}
