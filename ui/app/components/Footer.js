import React from "react";
import { Col, Row } from "react-bootstrap";

export default () =>
  <footer>
    <Row>
      <Col md={4}>
        <a href="https://www.hotosm.org/contact-us">Contact Us</a>
      </Col>
      <Col md={4} className="center">
        Made with ❤️ by <a href="https://www.hotosm.org/">HOT</a> and friends
      </Col>
      <Col md={4} className="right">
        <i className="fa fa-github" />{" "}
        <a href="https://github.com/hotosm/osm-export-tool2">Fork the Code</a>
      </Col>
    </Row>
  </footer>;
