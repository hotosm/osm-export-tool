import React from "react";
import { Link } from "react-router-dom";
import { Jumbotron, Row, Col, Alert } from 'react-bootstrap';

export default () =>
  <div className="help">
    <ol className="breadcrumb">
      <li>
        <Link to="/help">Help</Link>
      </li>
      <li className="active">Quick Start</li>
    </ol>
    <Jumbotron className="hero">
      <h1>Quick Start</h1>
      <p>Creating your first Export</p>
    </Jumbotron>
    <div className="helpDetailContainer">
      <section className="helpDetailBody">
        <Row>
          <Col sm={8}>
            <Alert bsStyle="warning">
              Registering an account is required to create an export. You can register through your OpenStreetMap account here with a valid email address.
            </Alert>
            <h2>1. Defining an Area of Interest</h2>
            <h2>2. Naming and Describing your Export</h2>
            <p>
              <strong>Describe Export:</strong> Enter the name, description and
              project (optional) of the new export. Select the area of interest on
              the map (right section).
            </p>
            <h2>3. Choosing File Formats</h2> 
            <h2>4. Choosing Map Features</h2>
            <h2>5. Downloading your Files</h2>
          </Col>
          <Col sm={3} smOffset={1} className="helpToc">
            <h3>IN THIS AREA</h3>
            <ul>
              <li>1. Defining an Area of Interest</li>
              <li>2. Naming and Describing your Export</li>
              <li>3. Choosing File Formats</li>
              <li>4. Choosing Map Features</li>
              <li>5. Downloading your Files</li>
            </ul>
          </Col>
        </Row>
      </section>
    </div>
  </div>;
