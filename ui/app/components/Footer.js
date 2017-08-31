import React from "react";
import { Col, Row } from "react-bootstrap";

export default () =>
  <footer>
    <Row>
      <Col md={4}>
        <i className="fa fa-envelope-o" />{" "}
        <a href="mailto:sysadmin@hotosm.org">Contact Us</a>
      </Col>
      <Col md={4} className="center">
        Made with ❤️ &nbsp; by <a href="https://www.hotosm.org/">HOT</a> and <a href="https://github.com/hotosm/osm-export-tool2/graphs/contributors">friends</a>
      </Col>
      <Col md={4} className="right">
        <i className="fa fa-github" />{" "}
        <a href="https://github.com/hotosm/osm-export-tool2">Fork the Code</a>
      </Col>
    </Row>
  </footer>;
