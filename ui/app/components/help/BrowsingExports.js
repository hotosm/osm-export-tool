import React from "react";
import { Link } from "react-router-dom";
import { Jumbotron, Row, Col, Alert } from 'react-bootstrap';

export default () =>
  <div className="help">
    <ol className="breadcrumb">
      <li>
        <Link to="/learn">Learn</Link>
      </li>
      <li className="active">Browsing Exports</li>
    </ol>
    <Jumbotron className="hero">
      <h1>Browsing Exports</h1>
      <p>
        Find and re-use exports created by other users and humanitarian organizations.
      </p>
    </Jumbotron>
    <div className="helpDetailContainer">
      <section className="helpDetailBody">
        <Row>
          <Col sm={8}>
            <h2 id="overview">Overview</h2>
            <p>
              If you're mapping as part of a humanitarian effort, it's possible that someone has already created an export relevant to your project.
              Browsing and downloading exports doesn't require a user account.
            </p>

            <h2 id="exportslist">Exports List</h2>
            <img src="/static/ui/images/docs/searchexports.png" style={{width:"100%"}}></img>
            <ol>
              <li>
                <strong>Search Box:</strong> Enter a query that will be matched against the Name, Description or Project of an export.
              </li>
              <li>
                <strong>Only my Exports:</strong> If you're logged in, display only exports created by you.
              </li>
            </ol>


            <h2 id="exportdetails">Export Details</h2>
            <img src="/static/ui/images/docs/exportdetail.png" style={{width:"100%"}}></img>
            <p>
              <strong>Left Panel: Export Details.</strong> Shows the date of creation, user who created the export, and the feature selection.
            </p>
            <p>
              <strong>Center Panel: Export Runs.</strong> Each "Run" of the export is associated with a list of file downloads, one for each export file format.
            </p>

            <h2 id="rerunexport">Re-running an Export</h2>
            <img src="/static/ui/images/docs/rerunclone.png" style={{width:"50%"}}></img>
            <p>
                “Re-running” an export lets you extract data using the same settings of the area, description, file formats and feature selection. 
                This function is generally used to obtain updated OSM data, including any added or modified information since the export was last run. 
                This is important to ensure that the information is current as OSM is constantly changing. 
                You will need to authenticate with an account to re-run an export.
            </p>
        
            <h2 id="cloneexport">Cloning an Export</h2>
            <p>
              "Cloning" an export lets you create a new export based on an existing one, possibly using the same area, description or feature selection,
               with the capability to modify each setting to suit your needs.
              For more details on the Create Export form, see the documentation : <Link to="/learn/quick_start">Quick Start</Link>.
            </p>
          </Col>
          <Col sm={3} smOffset={1} className="helpToc">
            <h3>IN THIS AREA</h3>
            <ul>
              <li><a href="#overview">Overview</a></li>
              <li><a href="#exportlist">Export List</a></li>
              <li><a href="#exportdetails">Export Details</a></li>
              <li><a href="#rerunexport">Re-running an Export</a></li>
              <li><a href="#cloneexport">Cloning an Export</a></li>
            </ul>
          </Col>
        </Row>
      </section>
    </div>
  </div>;
