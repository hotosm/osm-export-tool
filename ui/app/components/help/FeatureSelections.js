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
            <h3>Overview</h3>
            <p>
              OpenStreetMap is a planet-scale database of tagged geographic features.
              There are three types of OpenStreetMap entities:
              <ul>
                <li>Nodes, which represent a point on the surface of the earth.</li>
                <li>Ways, which are sets of nodes that can form lines or polygons.</li>
                <li>Relations, which are sets of nodes, ways or other relations.</li>
              </ul>
              Each of these three types of entities can have any number of key/value tags.
              For example, a post office may be represented by a way with tags building=yes and amenity=post_office.
            </p>
            <p>
              When we want to select part of OSM to use in our own projects, we must select:
              <ul>
                <li>A geographic query area.</li>
                <li>a <strong>Tag Filter</strong>, or a subset of OSM features we are interested in.
                  For example, when mapping buildings we want to limit our exports to only ways and relations that are tagged building=true.</li>
                <li>a <strong>Key Selection</strong>, or a subset of OSM keys we are interested in. 
                    At the present, there are tens of thousands of different OSM keys in use, so we only want the relevant ones.
                    Additionally, many useful GIS formats require a fixed tabular schema where each feature has a known set of columns.
                    For example, when mapping buildings we may also want to select the keys name and amenity, as these contain useful information.</li>
              </ul>
            </p>
            <p>
              The Export Tool provides two facilities for defining Tag Filters and Key Selections.
              <ul>
                <li>The <strong>Tag Tree</strong> is for common use cases, presenting a curated set of filters and selections.</li>
                <li>The <strong>YAML</strong> format provides complete control over filters and selections, using a SQL-like filter definition.</li>
              </ul>
            </p>
            <h3>Tag Tree</h3>
            <img src="/static/ui/images/docs/tagtree.png" style={{width:"75%"}}></img>
            <h3>Defining YAML when Creating an Export</h3>
            <p>
              YAML can be defined via the "Select Features" tab when creating an export. This can be edited inline or copy-pasted from a local file on your computer.
              Please note that YAML is whitespace-sensitive. For more information on the YAML format, see the  <Link to="/help/yaml">YAML Documentation</Link>.
            </p>
            <h3>Saving YAML as a Configuration</h3>
            <p>
              YAML can be defined and saved for future re-use via the Configurations page. It's useful to create one Configuration for a project which is then used
              on all exports related to that project. Give your Configuration a name and description that will make it discoverable by other mappers. 
              Unchecking the "Public" checkbox will make your Configuration only visible to yourself. Notably, Configurations can be edited, so this is useful for 
              evolving a feature selection during the course of a project, e.g. adding additional key selections.
            </p>
            <h3>Re-using a Configuration when Creating an Export</h3>
            <p>
              Saved Configurations can be selected via the "Stored Configuration" option on the Select Features tab when Creating an Export. Use the Search bar to find
              configurations related to your project.
            </p>
            <h3>More Resources</h3>
            <ul>
              <li><Link to="http://wiki.openstreetmap.org/wiki/Humanitarian_OSM_Tags">OpenStreetMap Wiki | Humanitarian OSM Tags</Link></li>
              <li><Link to="http://wiki.openstreetmap.org/wiki/Map_Features">OpenstreetMap Wiki | OSM Tags</Link></li>
            </ul>
          </Col>
          <Col sm={3} smOffset={1} className="helpToc">
            <h3>IN THIS AREA</h3>
            <ul>
              <li>Overview</li>
              <li>Tag Tree</li>
              <li>Defining YAML when Creating an Export</li>
              <li>Saving YAML as a Configuration</li>
              <li>Re-using a Configuration when Creating an Export</li>
              <li>More Resources</li>
            </ul>
          </Col>
        </Row>
      </section>
    </div>
  </div>;
