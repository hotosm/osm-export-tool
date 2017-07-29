import React from "react";
import { Link } from "react-router-dom";
import { Jumbotron, Row, Col, Alert } from 'react-bootstrap';

export default () =>
  <div className="help">
    <ol className="breadcrumb">
      <li><Link to="/help">Help</Link></li>
      <li className="active">Feature Selections</li>
    </ol>
    <Jumbotron className="hero">
      <h1>Selecting Features</h1>
      <p>
      </p>
    </Jumbotron>
    <div className="helpDetailContainer">
      <section className="helpDetailBody">
        <Row>
          <Col sm={8}>
            <p>
              The user can choose specific map features such as roads, buildings and
              water sources for download by selecting tags from the 'Tree Tag' tab or
              by uploading/selecting a preset file in the 'Preset File' tab. This help
              page will provide guidance to the user on how to use both of these
              functions available on the the 'Create' page to select their desired
              feature tags to export as map data.
            </p>

            <h3>Tree Tag</h3>
            <p>
              Interactively selecting features from the 'Tree Tag' tab is part of the
              'Export Wizard' on the 'Create' page that takes the user through the
              steps to create a new export, it can only be accessed once the previous
              nessessary steps have been completed. The 'Tree Tag' tab provides the
              user with two trees to select features from: Humanitarian Data Model
              (HDM) and the OpenStreetMap (OSM).
            </p>

            <p>
              HDM was developed and is aimed at reconciling schemas from humanitarian
              response agencies, as OSM was traditionally developed for mapping in
              nonemergency situations. Humanitarian field responders need to know how
              OSM tags relate to their existing data models, and how to include
              features that may be relevant only in disaster response, recovery, or
              development contexts.
            </p>
            <p>
              <a
                href="http://wiki.openstreetmap.org/wiki/Humanitarian_OSM_Tags"
                target="_blank"
              >
                OpenStreetMap Wiki | Humanitarian OSM Tags
              </a>
            </p>
            <p>
              OSM represents physical features on the ground using tags attached to
              its basic data structures such as its nodes, ways, and relations. Each
              tag describes a geographic attribute of the feature being shown by that
              specific node, way or relation.
            </p>
            <p>
              <a
                href="http://wiki.openstreetmap.org/wiki/Map_Features"
                target="_blank"
              >
                OpenstreetMap Wiki | OSM Tags
              </a>
            </p>
            <h4>Step by Step</h4>
            <ul>
              <li>
                Top-level branches can be expanded by clicking on the name of those
                with a plus-sign + to the left.
              </li>
              <li>Tick the box on the right to select a feature tag for export.</li>
              <li>Tick a top level-branch to select all sub-level for export.</li>
              <li>
                Tick the HDM or OSM top-level to select all features in either tree
                for export.
              </li>
              <li>
                Features from both the HDM and OSM can not be mixed. Once one is
                selected the other will be deactivated.
              </li>
            </ul>
            <h3>Preset File</h3>
            <p>
              Files can be uploaded on the 'Preset File' tab of the 'Create' page. As
              it is part of the 'Export Wizard' that takes the user through creating a
              new export, it can also only be accessed once the previous steps have
              been completed. The 'Preset File' tab provides the user with two options
              to apply a preset to the selected area of interest in order to export
              specific features: Upload Preset and 'Select Stored Preset.
            </p>
            <h4>Upload Preset</h4>
            <p>
              The 'Select Preset' tab provides the user with a text box to enter a
              'Filename'. Once this has been completed, the user can choose to either
              search their desktop for the file by clicking 'Upload a Preset' or
              select a file from saved presets by clicking 'Select Stored Preset.
            </p>
            <p>
              The 'Upload Preset' button will bring up a browse window for your
              desktop, where you can navigate to your desired file. Select the file,
              which will then be listed at the bottom of the 'Select Preset' tab on
              the 'Create' page. Check that this is the correct presest file and then
              click the green 'Upload' button.
            </p>
            <h4>Select Stored Preset</h4>
            <p>
              The 'Select Stored Preset' button opens a pop-up version of the
              'Presets' page, where the preset files can be filtered, searched and
              selected for use. Simply tick the desired box under the 'Select' column
              and click the 'Select' button at the bottom right corner of the window.
            </p>
            <p>
              The pop-up window will close and the selected preset will be loaded
              automatically into the 'Select Preset' tab, with the file listed at the
              bottom of the page. The user can then choose whether to publish the
              preset for everyone to access by clicking 'Publish this preset publicly'.
            </p>
          </Col>
        </Row>
      </section>
    </div>
  </div>;
