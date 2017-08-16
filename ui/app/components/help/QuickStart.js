import React from "react";
import { Link } from "react-router-dom";
import { Jumbotron, Row, Col, Alert } from 'react-bootstrap';

import drawAOI from "../../images/docs/drawaoi.png";
import describeExport from "../../images/docs/describeexport.png";
import exportFormats from "../../images/docs/exportformats.png";
import selectFeatures from "../../images/docs/selectfeatures.png";
import downloadFiles from "../../images/docs/downloadfiles.png";

export default () =>
  <div className="help">
    <ol className="breadcrumb">
      <li>
        <Link to="/learn">Learn</Link>
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
            <div>
              <h2 id="overview">Overview</h2>
              <p>
                Anyone can create a custom OpenStreetMap epxort with the Export Tool - just register an account. You can register with an OpenStreetMap account from <Link to="https://openstreetmap.org">OpenStreetMap.org</Link> and a valid email address.
              </p>
            </div>
            <div>
              <h2 id="step1">1. Defining an Area of Interest</h2>
              <img src={drawAOI} style={{width:"50%"}} /><br/>
              There are 4 ways to define an Area of Interest for your export:
              <ul>
                <li>
                  <strong>Search Bar:</strong> input a minX,minY,maxX,maxY string into the search bar. This will define a rectangular area of interest.
                </li>
                <li>
                  <strong>Bounding Box: </strong> Use the "Box" tool to the right to click and drag a rectangle,
                  or use the "Current View" tool to match the map's viewport.
                </li>
                <li>
                  <strong>Draw Polygon:</strong> Draw a freeform polygon. This must be a simple (not multi-) polygon.
                </li>
                <li>
                  <strong>Current View:</strong> Use "Current View" to match the map's viewport.
                </li>
                <li>
                  <strong>Upload:</strong> By uploading a GeoJSON polygon in WGS84 (geographic) coordinates.
                </li>
              </ul>
              <Alert bsStyle="warning">
                Uploaded geometries will be simplified to be 500 points or less.
              </Alert>
            </div>
            <div>
              <h2 id="step2">2. Naming and Describing your Export</h2>
              <img src={describeExport} style={{width:"50%"}} />
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
            </div>
            <div>
              <h2 id="step3">3. Choosing File Formats</h2>
              <img src={exportFormats} style={{width:"50%"}} />
              <p>
                Check at least one file format to export.
                To learn more about each individual format, read the documentation: <Link to="/learn/export_formats">Export Formats</Link>
              </p>
            </div>
            <div>
              <h2 id="step4">4. Choosing Map Features</h2>
              <img src={selectFeatures} style={{width:"50%"}} /><br/>
              <p>
                For your first time using the export tool, it's recommended to use the Tag Tree, which curates a set of filters and tags for common map features.
                As an example, check the box "Buildings" to create an export of all building geometries, as well as related data such as name and address keys.
              </p>
              <p>
                For more information about feature selection, see the documentation: <Link to="/learn/feature_selections">Feature Selections</Link>
              </p>
            </div>
            <div>
              <h2 id="step5">5. Downloading your Files</h2>
              <img src={downloadFiles} style={{width:"100%"}} /><br/>
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
            </div>
          </Col>
          <Col sm={3} smOffset={1} className="helpToc">
            <h3>IN THIS AREA</h3>
            <ul>
              <li><a href="#overview">Overview</a></li>
              <li><a href="#step1">1. Defining an Area of Interest</a></li>
              <li><a href="#step2">2. Naming and Describing your Export</a></li>
              <li><a href="#step3">3. Choosing File Formats</a></li>
              <li><a href="#step4">4. Choosing Map Features</a></li>
              <li><a href="#step5">5. Downloading your Files</a></li>
            </ul>
          </Col>
        </Row>
      </section>
    </div>
  </div>;
