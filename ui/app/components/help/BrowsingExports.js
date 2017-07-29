import React from "react";
import { Link } from "react-router-dom";
import { Jumbotron, Row, Col, Alert } from 'react-bootstrap';

export default () =>
  <div className="help">
    <ol className="breadcrumb">
      <li>
        <Link to="/help">Help</Link>
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
            <p>
              The{" "}
              <Link to="/exports" target="_blank">
                Exports
              </Link>{" "}
              page is where the user can filter and search existing saved exports, and
              either rerun or clone it. Please note an account is not needed view or
              search for existing exports, but is required to rerun.
            </p>

            <h3>Filter Options</h3>
            <p>
              The Exports page has several filtering options to make it eaiser to find
              the right export. The following filter options are detailed below:
            </p>
            <ol>
              <li>
                <strong>Search Box:</strong> Enter Name/Description/Event/Username
                keywords to filter.
              </li>
              <li>
                <strong>Start Date/End Date:</strong> Filter based on date of
                creation.
              </li>
              <li>
                <strong>Reset Form:</strong> Reset the filter options.
              </li>
              <li>
                <strong>Interactive Map:</strong> Visually displays location of
                filtered exports and can also be used to filter geographically by
                selecting on the map.
              </li>
              <li>
                <strong>Zoom Icon:</strong> Zoom to the location of the export on the
                interactive map.
              </li>
              <li>
                <strong>Eye Icon:</strong> Toggle the visibility of the export on the
                interactive map. This will hide an export that might be overlapping
                another.
              </li>
              <li>
                <strong>My Exports:</strong> Displays private exports if the user is
                logged in.
              </li>
              <li>
                <strong>Next:</strong> Move on to the next page to display more
                results.
              </li>
            </ol>


            <h3>Export Details</h3>
            <p>
              The user will be redirected to the 'Export Details' page once they have
              selected a saved export from the 'Exports' page. The 'Export Details'
              contains the information and status of the export, including the history
              of runs.
            </p>

            <p>
              The OSM features applied to the export can be viewed by clicking the
              'Features' button at the bottom of the page. If the features were
              selected using the 'Tree Tag', this will be replicated in a pop-up
              window. If a 'Preset File' was used then the features selected will be
              listed in the XML file.
            </p>

            <p>
              There are several options available on this page to apply to the Export,
              which include the ability to 'Rerun Export', 'Clone Export', or 'Delete
              Export'. The functionality of these options are detailed below:
            </p>

            <ol>
              <li>
                <strong>Re-run Export:</strong> This function will rerun the export
                with the original area of interest and settings for feature tags and
                file formats.
              </li>
              <li>
                <strong>Clone Export:</strong> This function will clone the export,
                maintaining the original area of interest but allows the user to
                modify the settings for feature tags and file formats.
              </li>
              <li>
                <strong>Delete Export:</strong> Delete the saved export. Please note
                that this function is only available to the user who originally
                created the export.
              </li>
            </ol>
          </Col>
          <Col sm={3} smOffset={1} className="helpToc">
            <h3>IN THIS AREA</h3>
            <ul>
            </ul>
          </Col>
        </Row>
      </section>
    </div>
  </div>;
