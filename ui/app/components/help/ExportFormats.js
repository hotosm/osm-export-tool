import React from "react";
import { Link } from "react-router-dom";
import { Jumbotron, Row, Col, Alert } from "react-bootstrap";

export default () =>
  <div className="help">
    <ol className="breadcrumb">
      <li><Link to="/learn">Learn</Link></li>
      <li className="active">Export Formats</li>
    </ol>
    <Jumbotron className="hero">
      <h1>Export Formats</h1>
      <p />
    </Jumbotron>
    <div className="helpDetailContainer">
      <section className="helpDetailBody">
        <Row>
          <Col sm={8}>
            <div>
              <h2 id="shp">Shapefile .shp</h2>
              <p>
                Shapefiles are a tabular format developed by Esri. They are the
                most popular file format for GIS data. A shapefile is actually 3-4
                individual files, commonly bundled together as a ZIP archive:
              </p>
              <ul>
                <li><strong>.shp</strong> - shape format; feature geometry</li>
                <li><strong>.shx</strong> - index format; positional index</li>
                <li><strong>.dbf</strong> - attribute format; columnar information</li>
                <li><strong>.prj</strong> - coordinate format; projection information</li>
              </ul>

              <p>
                Choose to export Shapefiles if you need the broadest compatibilty
                among GIS software.{" "}
              </p>
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
              <Alert bsStyle="warning">
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
                    ArcGIS Online - Shapefiles
                  </a>
                </li>
                <li>
                  <a
                    href="https://wiki.openstreetmap.org/wiki/Shapefiles#About_Shapefiles"
                    target="_blank"
                  >
                    OpenStreetMap Wiki - Esri SHP File
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h2 id="gpkg">Geopackage .gpkg</h2>
              <p>
                OGC Geopackages store geospatial data in a single SQLite database.
                Geopackages are very similar to Spatialite-enabled SQLite
                databases. They should be usable in most major GIS applications.
                Geopackages support practically unlimited file sizes and numbers
                of columns in tables, and have full support for Unicode. They're
                especially ideal if you need to run SQL queries over the data.
              </p>
              <h4>
                <strong>Compatible Software</strong>
              </h4>
              <ul>
                <li>PostgreSQL, SQL databases via GDAL/OGR</li>
                <li>QGIS</li>
                <li>Microsoft Access</li>
              </ul>
              <h4>
                <strong>Further Information</strong>
              </h4>
              <ul>
                <li>
                  <a href="http://www.geopackage.org/spec/" target="_blank">
                    OGC® GeoPackage Encoding Standard
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h2 id="gpkg">GeoJSON  .geojson</h2>
              <p>
              GeoJSON is an open standard geospatial data interchange format that represents simple geographic features and their nonspatial attributes. Based on JavaScript Object Notation (JSON), GeoJSON is a format for encoding a variety of geographic data structures. It uses a geographic coordinate reference system, World Geodetic System 1984, and units of decimal degrees.
              </p>
              <h4>
                <strong>Compatible Software</strong>
              </h4>
              <ul>
                <li>QGIS</li>
                <li>ArcGIS</li>
                <li>Mapbox</li>
                <li>Leaflet</li>
              </ul>
              <strong>Limitations</strong>
              <ul>
                <li>Size limit is dependent on the capabilities of the software being used
</li>
                <li>Not suitable for large datasets or complex spatial analyses due to its lack of indexing and projection information.</li>
              </ul>
              <h4>
                <strong>Further Information</strong>
              </h4>
              <ul>
                <li>
                  <a href="https://en.wikipedia.org/wiki/GeoJSON" target="_blank">
                  GeoJSON Wiki
                  </a>
                </li>
                <li>
                  <a href="https://datatracker.ietf.org/doc/html/rfc7946" target="_blank">
                  GeoJSON Specification
                  </a>
                </li>
                <li>
                  <a href="http://geojsonlint.com/" target="_blank">
                  GeoJSONLint
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h2 id="gpkg">FlatGeobuf .fgb</h2>
              <p>
              FlatGeobuf is a binary file format for storing geospatial vector data in a compact and efficient manner. It uses a hierarchical structure to organize features into layers, and stores attribute data in a separate file.
              </p>
              <h4>
                <strong>Compatible Software</strong>
              </h4>
              <ul>
                <li>QGIS</li>
                <li>Mapbox</li>
                <li>Leaflet</li>
                <li>PostGIS</li>
              </ul>
              <strong>Limitations</strong>
              <ul>
                <li>Not all GIS software supports FlatGeobuf natively, which may require additional tools or plugins to use.</li>
                <li>Lacks support for complex geometry types and some spatial operations.</li>
                <li>Requires additional processing to work with other non-binary formats, such as CSV or GeoJSON.</li>
              </ul>
              <h4>
                <strong>Further Information</strong>
              </h4>
              <ul>
                <li>
                  <a href="https://flatgeobuf.org/docs/" target="_blank">
                  FlatGeobuf documentation
                  </a>
                </li>
                <li>
                  <a href="https://flatgeobuf.org/spec/" target="_blank">
                  FlatGeobuf specification
                  </a>
                </li>
                <li>
                  <a href="https://github.com/flatgeobuf/flatgeobuf" target="_blank">
                  FlatGeobuf on GitHub
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h2 id="gpkg">CSV .csv</h2>
              <p>
              CSV is a file format for storing tabular data in plain text format. Each row of data represents a record, and each column represents a field of that record. CSV files are widely used because they are simple and easy to create and manipulate, making them a popular choice for data exchange.              </p>
              <h4>
                <strong>Compatible Software</strong>
              </h4>
              <ul>
                <li>Microsoft Excel</li>
                <li>OpenOffice Calc</li>
                <li>Google Sheets</li>
                <li>R or Python programming languages</li>
              </ul>
              <strong>Limitations</strong>
              <ul>
                <li>Does not support hierarchical data structures</li>
                <li>Does not support data typing, meaning that all values are treated as strings</li>
                <li>Does not include any metadata or schema information</li>
                </ul>
            </div>
            <div>
              <h2 id="gpkg">SQL .sql</h2>
              <p>
              SQL files are plain text files that contain SQL commands to create, modify or interact with a relational database. They can be used to define database schemas, constraints, and indexes, as well as to insert, update, and query data.
              </p>
              <h4>
                <strong>Compatible Software</strong>
              </h4>
              <ul>
                <li>MySQL</li>
                <li>Oracle Database</li>
                <li>Microsoft SQL Server</li>
                <li>PostgreSQL</li>
                <li>SQLite</li>
              </ul>
              <strong>Limitations</strong>
              <ul>
                <li>SQL files do not contain data themselves, but rather commands to manipulate data in a database</li>
                <li>May require additional tools or plugins to visualise or work with data in other software or file formats</li>
                <li>Performance can be impacted by the complexity and size of the data being queried</li>
              </ul>
              <h4>
                <strong>Further Information</strong>
              </h4>
              <ul>
                <li>
                  <a href="https://www.w3schools.com/sql/" target="_blank">
                  W3Schools SQL documentation
                  </a>
                </li>
                <li>
                  <a href="https://dev.mysql.com/doc/" target="_blank">
                  MySQL documentation
                  </a>
                </li>
                <li>
                  <a href="https://www.postgresql.org/docs/" target="_blank">
                  PostgreSQL documentation
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h2 id="img">Garmin .img</h2>
              <p>
                A .IMG file contains all information needed to render a map on a
                Garmin GPS mobile device. A .IMG is a disk image containing
                several files:
              </p>
              <ul>
                <li><strong>.rgn</strong> - map elements; polylines, polygons and points</li>
                <li><strong>.lbl</strong> - labels; map elements, city names, localities, etc</li>
                <li><strong>.tre</strong> - map structure information; data tree</li>
                <li><strong>.net</strong> - road network information</li>
                <li><strong>.nod</strong> - routing information</li>
                <li><strong>.mdr</strong> - searchable address table for routing desinations</li>
              </ul>
              <Alert bsStyle="warning">
                <strong>.IMG Styles:</strong> The cartographic style and feature
                choices of the map are not dependent on the feature selection
                submitted to the Export Tool - instead, a default style based on
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
                    SourceForge - Garmin IMG Format
                  </a>
                </li>
                <li>
                  <a
                    href="https://wiki.openstreetmap.org/wiki/OSM_Map_On_Garmin/IMG_File_Format"
                    target="_blank"
                  >
                    OpenStreetMap Wiki - Garmin IMG File
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h2 id="kmz">Google Earth .kml</h2>
              <p>
                The KMZ file is a compressed version of a KML file. KML is an
                XML-based foramt for modeling points, lines, polygons and
                associated attributes.
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
                    Google Earth - KML File
                  </a>
                </li>
                <li>
                  <a
                    href="https://developers.google.com/kml/documentation/kml_tut?hl=en"
                    target="_blank"
                  >
                    Google Documentation - KML Tutorial
                  </a>
                </li>
                <li>
                  <a href="https://wiki.openstreetmap.org/wiki/KML" target="_blank">
                    OpenStreetMap Wiki - KML File
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h2 id="pbf">OSM .pbf</h2>
              <p>
                OpenStreetMap's canonical data format is an XML document of nodes,
                ways and relations. The{" "}
                <strong>Protocol Buffer Binary Format (PBF)</strong> is an
                optimised representation of OSM XML, which is smaller on disk and
                faster to read. This format is only compatible with OpenStreetMap
                specific tools, such as OSM editing software. Each .PBF provided
                by the export tool should be referentially complete - that is, any
                node, way or relation referenced by a way or relation will appear
                in the PBF.
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
                <strong>Technical Note:</strong> Because .PBFs from the Export
                Tool are saved directly from Overpass, file boundaries match the
                rectangular bounds of the selected area and features are not
                clipped.
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
                    OpenStreetMap Wiki - PBF Format
                  </a>
                </li>
                <li>
                  <a
                    href="http://wiki.openstreetmap.org/wiki/Planet.osm"
                    target="_blank"
                  >
                    OpenStreetMap Wiki - Planet.osm
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h2 id="mwm">MAPS.ME .mwm</h2>
              <p>
                Maps.me is a GPS Navigation and map application for Android and
                iOS smartphones and tablets, notably supporting offline mapping
                and navigation.
              </p>
              <p>To use a custom export with Maps.me on Android, follow these steps:</p>
              <ol>
                <li>Open Maps.me and navigate to your region of interest</li>
                <li>Accept Maps.me's prompt and download the proffered region</li>
                <li>Force close Maps.me</li>
                <li>Create an MWM export</li>
                <li>Download the export, unzip it, and copy the <code>.mwm</code> file to your device</li>
                <li>Using the Android File Manager, navigate to the location containing the <code>.mwm</code> file</li>
                <li>Long-press to select it and touch the "copy" or "cut" button</li>
                <li>Navigate to "MapsWithMe" and open the highest numbered folder (e.g. <code>170917</code>)</li>
                <li>Copy/move your <code>.mwm</code> file into this directory by tapping the "paste" button</li>
                <li>Delete the existing <code>.mwm</code> file for your region of interest, taking note of its filename</li>
                <li>Rename your <code>.mwm</code> file to match the region that was downloaded by Maps.me (which you just deleted) by long-pressing (to select) and tapping the "more" button (3 vertical dots)</li>
                <li>Open Maps.me</li>
              </ol>
              <h4>
                <strong>Compatible Software</strong>
              </h4>
              <ul>
                <li>maps.me</li>
              </ul>
              <h4>
                <strong>Further Information</strong>
              </h4>
              <ul>
                <li>
                  <a href="http://maps.me/" target="_blank">
                    maps.me
                  </a>
                </li>
                <li>
                  <a href="https://github.com/mapsme/omim" target="_blank">
                    maps.me on GitHub
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h2 id="mbtiles">MBTiles .mbtiles</h2>
              <p>
                MBTiles is a file format for storing map tiles in a single file.
                The Export Tool allows users to create MBTiles containing tiles
                from OpenStreetMap, which can be used as sources of offline
                context within applications that support them.
              </p>
              <h4>
                <strong>Compatible Software</strong>
              </h4>
              <ul>
                <li><a href="http://posm.io/">POSM</a></li>
                <li><a href="https://josm.openstreetmap.de/">JOSM</a> (<a href="http://wiki.openstreetmap.org/wiki/JOSM/Plugins/Mbtiles">plugin</a>)</li>
                <li><a href="http://openmapkit.org/">OpenMapKit</a></li>
                <li>Others</li>
              </ul>
              <h4>
                <strong>Further Information</strong>
              </h4>
              <ul>
                <li>
                  <a href="https://www.mapbox.com/help/define-mbtiles/" target="_blank">
                    MBTiles on Mapbox
                  </a>
                </li>
                <li>
                  <a href="https://github.com/mapbox/mbtiles-spec" target="_blank">
                    MBTiles spec
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h2 id="bundle">POSM bundle</h2>
              <p>
                POSM bundles are intended for bootstrapping <a
                href="http://posm.io/" target="_blank">Portable
                OpenStreetMap</a> instances. Bundles are tarballs containing OSM
                PBFs (with all features in the area of interest) and any other
                formats that were selected.
              </p>
              <h4>
                <strong>Compatible Software</strong>
              </h4>
              <ul>
                <li><a href="http://posm.io/">POSM</a></li>
              </ul>
            </div>
          </Col>
          <Col sm={3} smOffset={1} className="helpToc">
            <h3>IN THIS AREA</h3>
            <ul>
              <li>
                <a href="#shp">Shapefile .shp</a>
              </li>
              <li>
                <a href="#gpkg">Geopackage .gpkg</a>
              </li>
              <li>
                <a href="#img">Garmin .img</a>
              </li>
              <li>
                <a href="#kmz">Google Earth .kml</a>
              </li>
              <li>
                <a href="#pbf">OSM .pbf</a>
              </li>
              <li>
                <a href="#obf">OSMAnd .obf</a>
              </li>
              <li>
                <a href="#mwm">MAPS.ME .mwm</a>
              </li>
              <li>
                <a href="#mtiles">MBTiles .mbtiles</a>
              </li>
              <li>
                <a href="#bundle">POSM bundle</a>
              </li>
            </ul>
          </Col>
        </Row>
      </section>
    </div>
  </div>;
