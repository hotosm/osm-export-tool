import React from "react";
import { Link } from "react-router-dom";
import { Jumbotron, Row, Col } from 'react-bootstrap';

import tagTree from "../../images/docs/tagtree.png";

export default () =>
  <div className="help">
    <ol className="breadcrumb">
      <li><Link to="/learn">Learn</Link></li>
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
            <h2 id="overview">Overview</h2>
            <p>
              OpenStreetMap is a planet-scale database of tagged geographic features.
              There are three types of OpenStreetMap entities:
              <ul>
                <li><strong>Nodes,</strong> which represent a point on the surface of the earth.</li>
                <li><strong>Ways,</strong> which are sets of nodes that can form lines or polygons.</li>
                <li><strong>Relations,</strong> which are sets of nodes, ways or other relations.</li>
              </ul>
              Each of these three types of entities can have any number of key/value tags.
              For example, a post office may be represented by a way with tags building=yes and amenity=post_office.
            </p>
            <p>
              When we want to select part of OSM to use in our own projects, we must select:
            </p>
            <ul>
              <li>A geographic query area.</li>
              <li>a <strong>Tag Filter</strong>, or a subset of OSM features we are interested in.
                For example, when mapping buildings we want to limit our exports to only ways and relations that are tagged building=true.</li>
              <li>a <strong>Key Selection</strong>, or a subset of OSM keys we are interested in.
                  At the present, there are tens of thousands of different OSM keys in use, so we only want the relevant ones.
                  Additionally, many useful GIS formats require a fixed tabular schema where each feature has a known set of columns.
                  For example, when mapping buildings we may also want to select the keys name and amenity, as these contain useful information.</li>
            </ul>
            <p>
              The Export Tool provides two facilities for defining Tag Filters and Key Selections.
              <ul>
                <li>The <strong>Tag Tree</strong> is for common use cases, presenting a curated set of filters and selections.</li>
                <li>The <strong>YAML</strong> format provides complete control over filters and selections, using a SQL-like filter definition.</li>
              </ul>
            </p>
            <h2 id="tagtree">Tag Tree</h2>
            <img src={tagTree} style={{width:"75%"}} />
            <p> The tag tree is the simplest way to get started selecting features.</p>
            <p>Each <strong>Parent Checkbox</strong> filters the data to a category of features, also including relevant tags.</p>
            <p>Each parent checkbox can expanded, and individual <strong>Child Checkboxes</strong> can be selected to further filter down the data.</p>
            <p>The <strong>Infobox</strong> on the right shows detailed information about the tags and filters specified by the hovered checkbox.</p>
            <p>The Tag Tree generates YAML, so you can preview the YAML document created by switching tabs.</p>
            <h2 id="yaml">Defining YAML when Creating an Export</h2>
            <p>
              YAML can be defined via the "Select Features" tab when creating an export. This can be edited inline or copy-pasted from a local file on your computer.
              Please note that YAML is whitespace-sensitive. For more information on the YAML format, see the documentation: <Link to="/learn/yaml">YAML Specification</Link>.
            </p>
            <h2 id="configuration">Saving YAML as a Configuration</h2>
            <p>
              YAML can be defined and saved for future re-use via the Configurations page. It's useful to create one Configuration for a project which is then used
              on all exports related to that project. Give your Configuration a name and description that will make it discoverable by other mappers.
              Unchecking the "Public" checkbox will make your Configuration only visible to yourself. Notably, Configurations can be edited, so this is useful for
              evolving a feature selection during the course of a project, e.g. adding additional key selections.
            </p>
            <h2 id="reuse">Re-using a Configuration when Creating an Export</h2>
            <p>
              Saved Configurations can be selected via the "Stored Configuration" option on the Select Features tab when Creating an Export. Use the Search bar to find
              configurations related to your project.
            </p>
            <h2 id="moreresources">More Resources</h2>
            <ul>
              <li><a href="http://wiki.openstreetmap.org/wiki/Humanitarian_OSM_Tags">OpenStreetMap Wiki - Humanitarian OSM Tags</a></li>
              <li><a href="http://wiki.openstreetmap.org/wiki/Map_Features">OpenstreetMap Wiki - OSM Tags</a></li>
            </ul>
          </Col>
          <Col sm={3} smOffset={1} className="helpToc">
            <h3>IN THIS AREA</h3>
            <ul>
              <li><a href="#overview">Overview</a></li>
              <li><a href="#tagtree">Tag Tree</a></li>
              <li><a href="#yaml">Defining YAML when Creating an Export</a></li>
              <li><a href="#configuration">Saving YAML as a Configuration</a></li>
              <li><a href="#reuse">Re-using a Configuration when Creating an Export</a></li>
              <li><a href="#moreresources">More Resources</a></li>
            </ul>
          </Col>
        </Row>
      </section>
    </div>
  </div>;
