import React from "react";
import { Link } from "react-router-dom";

export default () =>
  <div className="help">
    <ol className="breadcrumb">
      <li><Link to="/help">Help</Link></li>
      <li className="active">Export Formats</li>
    </ol>

    <h2>File Formats</h2>
    <div className="well">
      The OSM Export Tool allows the data selected by the user to be exported
      into any of the following five file formats: Esri SHP (OSM and Thematic),
      Garmin IMG, Google KMZ, OSM PBF, and SQLite SQL. This help page provides
      the user with information about these file formats. It also lists some
      external links where the user can find further information.
    </div>

    <a name="shp" />
    <h3>Esri SHP</h3>
    <div className="well">
      <p>
        The shapefile format developed by Esri spatially describes geometries as
        either 'points', 'polylines', or 'polygons' with a set of associated
        attributes. Similar to OSM these can be considered as 'nodes', 'ways',
        'closed ways', and 'relations' respectively. The shapefile is made up of
        several files formatted to represent different aspects of geodata:
      </p>
      <ul>
        <li>.shp - shape format; feature geometry</li>
        <li>.shx - index format; positional index</li>
        <li>.dbf - attribute format; columnar information</li>
        <li>.prj - coordinate format; projection information</li>
      </ul>
    </div>

    <h4>
      <strong>Schema Options</strong>
    </h4>
    <div className="well">
      <p>
        The data is available for download from the Export Tool in two different
        shapefile schema formats which are detailsed below:
      </p>
      <ul>
        <li>OSM </li>
        The OSM schema is the default shapefile export, which provides all the
        selected features for an area of interest in a single point, polyline
        and polygon table.
        <li>Thematic</li>
        <p>
          The HOT generated thematic schema provides the features selected for
          an area of interest in their individual point, polyline and polygon
          tables. The following{" "}
          <a
            href="http://wiki.openstreetmap.org/wiki/User:Bgirardot/How_To_Convert_osm_.pbf_files_to_Esri_Shapefiles"
            target="_blank"
          >
            process
          </a>{" "}
          has been applied to the selected data in order to split the features
          into their own tables for ease of use by the user.
        </p>
      </ul>
      <h4>
        <strong>Compatible Software</strong>
      </h4>
      <ul>
        <li>QGIS</li>
        <li>GRASS GIS</li>
        <li>ArcMap</li>
        <li>MapInfo</li>
      </ul>
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
    </div>

    <a name="img" />
    <h3>Garmin IMG</h3>
    <div className="well">
      <p>
        The image file contains all the information needed to render a map on a
        Garmin GPS unit. The hard-disk image is a flat file system complete with
        a partition table, that does not directly support the concept of
        subdirectories, but does provide a kind of sub-directory structure. The
        image file contains several subfiles:
      </p>
      <ul>
        <li>.rgn - map elements; polylines, polygons and points</li>
        <li>.lbl - labels; map elements, city names, localities, etc</li>
        <li>.tre - map structure information; data tree</li>
        <li>.net - road network information</li>
        <li>.nod - routing information</li>
        <li>.mdr - searchable address table for routing desinations</li>
      </ul>
      <h4>
        <strong>Compatible Software</strong>
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
    </div>

    <a name="kmz" />
    <h3>Google KMZ</h3>
    <div className="well">
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
    </div>

    <a name="pbf" />
    <h3>OSM Source PBF</h3>
    <div className="well">
      <p>
        The Protocolbuffer Binary Format (PBF) is a highly compressed optimisted
        format intended as an alternative to the XML, which are the two main
        formats of the OSM Planet file. The Planet.osm is the OSM data in one
        file with all the nodes, ways and relations that make up the map.
      </p>
      <h4>
        <strong>Compatible Software</strong>
      </h4>
      <ul>
        <li>JOSM</li>
        <li>Osmosis</li>
        <li>QGIS</li>
        <li>ArcMap</li>
      </ul>
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
    </div>

    <a name="obf" />
    <h3>OSMAnd OBF</h3>
    <div className="well">
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
    </div>

    <a name="sql" />
    <h3>SQLite SQL</h3>
    <div className="well">
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
    </div>
  </div>;
