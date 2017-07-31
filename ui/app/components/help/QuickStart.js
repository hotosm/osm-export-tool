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
            <img src="/static/ui/images/docs/drawaoi.png" style={{width:"50%"}}></img><br/>
            There are 4 ways to define an Area of Interest for your export:
            <ul>
              <li>
                By drawing a bounding box. Use the "Box" tool to the right to click and drag a rectangle,
                or use the "Current View" tool to match the map's viewport.
              </li>
              <li>
                By inputting a minX,minY,maxX,maxY string into the search bar. This will define a rectangular area of interest.
              </li>
              <li>
                By drawing a freeform polygon. This must be a simple (not multi-) polygon. 
              </li>
              <li>
                By uploading a GeoJSON polygon in WGS84 (geographic) coordinates.
              </li>
            </ul>
            <Alert bsStyle="warning">
              Uploaded geometries will be simplified to be 500 points or less. 
            </Alert>
              
            <h2>2. Naming and Describing your Export</h2>
            <img src="/static/ui/images/docs/describeexport.png" style={{width:"50%"}}></img>
            <ul>
              <li>
                <strong>Name (required):</strong> choose a short, descriptive name.
              </li>
              <li>
                <strong>Description:</strong> a longer text body, perhaps describing what relevant features the export includes.
              </li>
              <li>
                <strong>Project:</strong> Helps to group together exports particular to a project, e.g. "HOT Activation in Haiti"
              </li>
            </ul>
            <h2>3. Choosing File Formats</h2> 
            <img src="/static/ui/images/docs/exportformats.png" style={{width:"50%"}}></img>
            <p>
              Check at least one file format to export. To learn more about each individual format,
              read the <Link to="/help/export_formats">Export Formats documentation.</Link>

            </p>
            <h2>4. Choosing Map Features</h2>
            
            <h2>5. Downloading your Files</h2>
            <p>After you submit your export using <strong>Create Export</strong>,
            you will be redirected to the <strong>Export Detail Page</strong>,
            which shows a list of <strong>Export Runs</strong>. You'll see the first run at the top of the page.
            It will be in one of the following states:
            </p>
            <ul>
              <li><strong>Submitted: </strong> The export is waiting to be processed. This should be brief, depending on server load.</li>
              <li><strong>Running: </strong> The export is waiting to be processed. City-sized regions should be a few minutes - 
              larger regions can take upwards of 20 minutes, depending on the density of OSM data.</li>
              <li><strong>Completed: </strong> Your export files are available for download. Each export format has a separate download link for its ZIP archive.</li>
            </ul>
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
