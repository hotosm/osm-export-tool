import React from "react";
import { Link } from "react-router-dom";
import { Jumbotron, Row, Col, Alert } from 'react-bootstrap';

export default () =>
  <div className="help">
    <ol className="breadcrumb">
      <li><Link to="/help">Help</Link></li>
      <li className="active">Export Formats</li>
    </ol>
    <Jumbotron className="hero">
      <h1>Export Formats</h1>
      <p>
      </p>
    </Jumbotron>
    <div className="helpDetailContainer">
      <section className="helpDetailBody">
        <Row>
          <Col sm={8}>
            <h2 id="shp">Esri Shapefile (.SHP)</h2>
            <p>
              Shapefiles are a tabular format developed by Esri. They are the most popular file format for GIS data.
              A shapefile is actually 3-4 individual files, commonly bundled together as a ZIP archive:
            </p>
            <ul>
              <li>.shp - shape format; feature geometry</li>
              <li>.shx - index format; positional index</li>
              <li>.dbf - attribute format; columnar information</li>
              <li>.prj - coordinate format; projection information</li>
            </ul>

            <p>Choose to export Shapefiles if you need the broadest compatibilty among GIS software. </p>
            <ul>
              <li>QGIS</li>
              <li>GRASS GIS</li>
              <li>ArcMap</li>
              <li>MapInfo</li>
            </ul>

            <strong>Limitations</strong>
            <ul>
              <li>Size limit of 2 GB</li>
              <li>column name length limit of 10 characters</li>
            </ul>
            <Alert bsStyle="success">
              A Shapefile alternative without these limitations is <a href="#gpkg">Geopackage</a>.
            </Alert>
            <h4>
              <strong>Further Information</strong>
            </h4>
            <ul>
              <li>
                <a
                  href="https://doc.arcgis.com/en/arcgis-online/reference/shapefiles.htm"
                  target="_blank"
                >
                  ArcGIS Online | Shapefiles
                </a>
              </li>
              <li>
                <a
                  href="https://wiki.openstreetmap.org/wiki/Shapefiles#About_Shapefiles"
                  target="_blank"
                >
                  OpenStreetMap Wiki | Esri SHP File
                </a>
              </li>
            </ul>
          </Col>
        </Row>
        <Row>
          <Col xs={6}>
            <h2>Garmin .IMG</h2>
            <p>
              A .IMG file contains all information needed to render a map on a
              Garmin GPS mobile device. A .IMG is a disk image containing several files:
            </p>
            <ul>
              <li>.rgn - map elements; polylines, polygons and points</li>
              <li>.lbl - labels; map elements, city names, localities, etc</li>
              <li>.tre - map structure information; data tree</li>
              <li>.net - road network information</li>
              <li>.nod - routing information</li>
              <li>.mdr - searchable address table for routing desinations</li>
            </ul>
            <Alert bsStyle="warning">
              <strong>.IMG Styles:</strong> The cartographic style and feature choices of the map are not dependent 
              on the feature selection submitted to the Export Tool - instead, a default style based on
              all OSM data is used.
            </Alert>
            <h4>
              <strong>Compatible Hardware/Software</strong>
            </h4>
            <ul>
              <li>Garmin</li>
              <li>QLandkarte</li>
              <li>OSM Composer</li>
              <li>GroundTruth</li>
            </ul>
            <h4>
              <strong>Further Information</strong>
            </h4>
            <ul>
              <li>
                <a
                  href="http://sourceforge.net/projects/garmin-img/files/IMG%20File%20Format/1.0/imgformat-1.0.pdf/download"
                  target="_blank"
                >
                  SourceForge | Garmin IMG Format
                </a>
              </li>
              <li>
                <a
                  href="https://wiki.openstreetmap.org/wiki/OSM_Map_On_Garmin/IMG_File_Format"
                  target="_blank"
                >
                  OpenStreetMap Wiki | Garmin IMG File
                </a>
              </li>
            </ul>
          </Col>
        </Row>
        <Row>
          <Col xs={6}>
            <h2>Google KMZ</h2>
            <p>
              The KMZ file is a compressed version of a KML file. The Keyhole Markup
              Language (KML) is an Extensible Markup Language (XML) grammar and file
              format for modeling and storing geographic features such as points,
              lines, images polygons and models.
            </p>
            <h4>
              <strong>Compatible Software</strong>
            </h4>
            <ul>
              <li>Google Earth</li>
              <li>Google Maps</li>
              <li>QGIS</li>
              <li>ArcMap</li>
            </ul>
            <h4>
              <strong>Further Information</strong>
            </h4>
            <ul>
              <li>
                <a
                  href="https://support.google.com/earth/answer/148118?hl=en"
                  target="_blank"
                >
                  Google Earth | KML File
                </a>
              </li>
              <li>
                <a
                  href="https://developers.google.com/kml/documentation/kml_tut?hl=en"
                  target="_blank"
                >
                  Google Documentation | KML Tutorial
                </a>
              </li>
              <li>
                <a href="https://wiki.openstreetmap.org/wiki/KML" target="_blank">
                  OpenStreetMap Wiki | KML File
                </a>
              </li>
            </ul>
          </Col>
        </Row>
        <Row>
          <Col xs={6}>
            <h2>OpenStreetMap .PBF</h2>
            <p>
              OpenStreetMap's canonical data format is an XML document of nodes, ways and relations.
              The <strong>Protocol Buffer Binary Format (PBF)</strong> is an optimised representation of OSM XML,
              which is smaller on disk and faster to read. This format is only compatible with OpenStreetMap specific tools,
              such as OSM editing software. Each .PBF provided by the export tool should be referentially complete - that is,
              any node, way or relation referenced by a way or relation will appear in the PBF.
            </p>
            <h4>
              <strong>Compatible Software:</strong>
            </h4>
            <ul>
              <li>JOSM</li>
              <li>Osmosis</li>
              <li>QGIS</li>
              <li>ArcMap</li>
            </ul>
            <Alert bsStyle="warning">
              <strong>Technical Note:</strong> Because .PBFs from the Export Tool are saved directly from Overpass,
              file boundaries match the rectangular bounds of the selected area and features are not clipped.
            </Alert>
            <h4>
              <strong>Further Information</strong>
            </h4>
            <ul>
              <li>
                <a
                  href="https://wiki.openstreetmap.org/wiki/PBF_Format"
                  target="_blank"
                >
                  OpenStreetMap Wiki | PBF Format
                </a>
              </li>
              <li>
                <a
                  href="http://wiki.openstreetmap.org/wiki/Planet.osm"
                  target="_blank"
                >
                  OpenStreetMap Wiki | Planet.osm
                </a>
              </li>
            </ul>
          </Col>
        </Row>
        <Row>
          <Col xs={6}>
            <h2>OSMAnd OBF</h2>
            <p>
              OsmAnd is a GPS Navigation and map application that runs on many Android
              and iOS smartphones and tablets, featuring optional offline maps and
              turn by turn directions.
            </p>
            <h4>
              <strong>Compatible Software</strong>
            </h4>
            <ul>
              <li>OSMAnd</li>
            </ul>
            <h4>
              <strong>Further Information</strong>
            </h4>
            <ul>
              <li>
                <a href="http://wiki.openstreetmap.org/wiki/OsmAnd" target="_blank">
                  OSMAnd | OBF Format
                </a>
              </li>
            </ul>
          </Col>
        </Row>
        <Row>
          <Col xs={6}>
            <h2>OGC GeoPackage</h2>
            <p>
              The .sql file is related to the Structured Query Language (SQL) and are
              used to modify the contents of a relation database. These files written
              in ASCII may contain instructions and statements for creating or
              modifying database structure, such as data insertions, updates,
              deletions and other SQL operations.
            </p>
            <h4>
              <strong>Compatible Software</strong>
            </h4>
            <ul>
              <li>PostgreSQL</li>
              <li>MySQL</li>
              <li>Microsoft Access</li>
            </ul>
            <h4>
              <strong>Further Information</strong>
            </h4>
            <ul>
              <li>
                <a
                  href="http://www.postgresql.org/docs/9.4/static/sql.html"
                  target="_blank"
                >
                  PostgreSQL | The SQL Language
                </a>
              </li>
              <li>
                <a href="https://en.wikipedia.org/wiki/SQL" target="_blank">
                  Wikipedia | SQL
                </a>
              </li>
            </ul>
          </Col>
        </Row>
      </section>
    </div>
  </div>;
