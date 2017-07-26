import React from "react";
import { Link } from "react-router-dom";

export default () =>
  <div className="help">
    <a name="top" />
    <ol className="breadcrumb">
      <li><Link to="/help">Help</Link></li>
      <li className="active">Presets</li>
    </ol>

    <h2>Presets</h2>
    <div className="well">
      <p>
        The{" "}
        <Link to="/configurations" target="_blank">
          Presets
        </Link>{" "}
        page is where the user can filter and search existing saved preset
        files, as well as upload one from their local desktop. Please note an
        account is not needed to view or search existing presets, but is
        required to upload one and only the user who originally uploaded the
        preset can delete it.
      </p>

      <p>
        The user can use an XML preset file with the Export Tool to specify
        which features they would like to export from the selected area based on
        identified tags. This help page will provide step by step guidance for
        the 'Presets' page, and how to search, download, upload and customise
        presets.
      </p>
    </div>

    <a name="filter" />
    <h3>Filter Options:</h3>
    <div className="well">
      <p>
        The 'Presets' page has several filtering options to make it eaiser to
        find the right preset file. The following filter options are detailed
        below:
      </p>
      <ol>
        <li>
          <strong>Search Box:</strong> Filter presets by Name/Owner.
        </li>
        <li>
          <strong>Start Date/End Date:</strong> Filter based on date of
          creation.
        </li>
        <li>
          <strong>Reset Form:</strong> Reset the filter options.
        </li>
        <li>
          <strong>My Preset Files:</strong> Display personal preset files if the
          user is logged in.
        </li>
        <li>
          <strong>Next:</strong> Move on to display more results.
        </li>
      </ol>

      <a href="#top">top</a>
    </div>

    <a name="Download" />
    <h3>Download Preset:</h3>
    <div className="well">
      <p>
        To download a preset, the user must select the specific file under the
        'Download Configuration' column in the table, which will open the XML
        file in a new tab. Please note this does not download the preset
        automatically to your desktop. The user will have to maunally save the
        preset as a XML file.
      </p>

      <a href="#top">top</a>
    </div>

    <a name="Upload" />
    <h3>Upload Preset</h3>
    <div className="well">
      <p>
        To upload a preset, the user must enter a 'Filename' and click the
        'Upload Preset' button. This will bring up a search finder for your
        desktop, where you can navigate to your desired XML file and select it.
        The file will then be listed at the bottom right of the 'Presets' page.
        Check that this is the correct file and click the green 'Upload' button
        to add it.
      </p>

      <a href="#top">top</a>
    </div>

    <a name="Customise Preset" />
    <h3>Customise</h3>
    <div className="well">
      <p>
        To customise a preset, a user can use external software such as JOSM, or
        save their feature selection from the 'Tree Tag' tab on the 'Create'
        page.
      </p>
      <p>
        The link below will redirect you to the 'Creating Custom Presets' page
        in the 'JOSM - Detailed Editing' section of LearnOSM.
      </p>
      <ul>
        <li>
          <strong>LearnOSM:</strong>{" "}
          <a
            href="http://learnosm.org/en/josm/creating-presets/"
            target="_blank"
          >
            Creating Custom Presets
          </a>.
        </li>
      </ul>
      <p>
        To customise a preset file using the 'Tree Tag' tab as part of the
        'Export Wizard', you must go through the process of creating a new
        export.
      </p>
      <p>
        To save the tag selection for your customised preset file, make sure you
        tick either the 'Save feature selection privately' or the 'Publish
        feature selection publicly' button on the 'Export Summary' tab.
      </p>
      <p>
        Once the export has run, you can access your customised preset file from
        either the list of files on the right side of the 'Export Details' page
        or from the preset table on the 'Presets' page.
      </p>
      <ul>
        <li>
          <strong>Export Tool:</strong>{" "}
          <a href="{{ configurations_url }}" target="_blank">
            Presets
          </a>.
        </li>
      </ul>
      <a href="#top">top</a>
    </div>
  </div>;
