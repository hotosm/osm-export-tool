import React from "react";
import { Link } from "react-router-dom";

export default () =>
  <div className="help">
    <a name="top" />
    <ol className="breadcrumb">
      <li>
        <Link to="/help">Help</Link>
      </li>
      <li className="active">Create</li>
    </ol>

    <a name="create" />
    <h2>Create</h2>
    <div className="well">
      <p>
        The{" "}
        <Link to="/exports/new" target="_blank">
          Create
        </Link>{" "}
        page is where the user can select an area of interest, describe the
        export, select file formats and feature tags, load a preset file and
        specify to either keep the export private or share it publicly. Please
        note that an account is needed to create an export.
      </p>
    </div>
    <h3>Export Wizard</h3>
    <div className="well">
      <p>
        The 'Create' page is set up like a wizard so that the user is guided
        through the required steps to create an export. The user can not move on
        to the next section until they have completed the neccessary parts of
        the current section.
      </p>
      <p>
        Similarly, certain functionality will be locked if another method has
        been chosen, such as the 'Tree Tag' and 'Preset File'. These can not be
        both applied to the same export, and the use of one method will
        deactivate the other.
      </p>
      <p>
        There are five tabs that make up the 'Export Wizard' on the 'Create'
        page. These include the 'Describe Export', 'File Formats', 'Tree Tag',
        'Preset File' and 'Export Summary', which are detailed below:
      </p>
      <ol>
        <li>
          <strong>Describe Export:</strong> Enter the name, description and
          project (optional) of the new export. Select the area of interest on
          the map (right section).
        </li>
        <li>
          <strong>File Formats:</strong> Select one or more file format(s) for
          the export.
        </li>
        <li>
          <strong>Tree Tag:</strong> Expand and select features from the HDM or
          OSM tree tag for export and click 'Next'. Preset files on the next tab
          can not be used if tags are selected from either tree. Please see the{" "}
          <Link to="/help/features" target="_blank">
            Feature Selection
          </Link>{" "}
          help page for further information.
        </li>
        <li>
          <strong>Preset File:</strong> Select a preset file to apply to the
          export area by either specifying a name and loading a file from the
          desktop, or select a preset file from the saved presets. Tick the
          'Publish this preset publicly' button to share the loaded preset
          publicly and save it to the 'Presets' page.
        </li>
        <li>
          <strong>Export Summary:</strong> This tab provides an overview of the
          export settings, along with the options to 'Save feature selection
          privately', 'Publish feature selection publicly' and 'Publish export
          publicly'. Click 'Create Export' to complete and run the new export.
        </li>
      </ol>
      <a href="#top">top</a>
    </div>

    <h3>Export Details</h3>
    <div className="well">
      <p>
        The user will be redirected to the 'Export Details' page once they have
        clicked 'Create Export' and the export successfully runs. This page
        contains the details and status of the export, including the history of
        runs.
      </p>

      <p>
        The OSM features applied to the export can be viewed by clicking the
        'Export Features' button at the bottom of the page. If the features were
        selected using the 'Tree Tag', this will be replicated in a pop-up
        window. If a 'Preset File' was used then the features selected will be
        listed in the XML file.
      </p>

      <p>
        There are several options available on this page to apply to the Export,
        which include the ability to 'Rerun Export', 'Clone Export', or 'Delete
        Export'. The functionality of these options are detailed below:{" "}
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
      <a href="#top">top</a>
    </div>
  </div>;
