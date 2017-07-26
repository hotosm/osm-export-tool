import React from "react";
import { Link } from "react-router-dom";

export default () =>
  <div className="help">
    <a name="top" />
    <ol className="breadcrumb">
      <li><Link to="/help">Help</Link></li>
      <li className="active">Feature Selections</li>
    </ol>

    <h2>Feature Selections</h2>
    <div className="well">
      <p>
        Feature Selections define how OSM is transformed into other formats,
        such as Shapefile, SQLite/Geopackage and KML. Many of these formats are
        tabular, so we need to define a set of columns to fill with OSM data.
        This feature selection format is similar to style files used by programs
        such as{" "}
        <a href="http://wiki.openstreetmap.org/wiki/Osm2pgsql">osm2pgsql</a> and{" "}
        <a href="https://imposm.org">imposm</a>.
      </p>
      <p>A basic complete example of a feature selection with 3 themes:</p>
      <pre>
        buildings: types: - polygons select: - name - building where: building
        IS NOT NULL waterways: types: - lines - polygons select: - name -
        waterway where: natural IN ('waterway') hospitals: select: - name -
        amenity where: amenity = "hospital"
      </pre>

      <h4>The YAML format:</h4>
      <ul>
        <li>
          Is whitespace sensitive. Each child element must be indented below its
          parent element.
        </li>
        <li>
          Has two data structures: lists and mappings. In the above example,{" "}
          <code>buildings</code>, <code>types</code>, <code>select</code> are
          examples of keys in mappings.
        </li>
        <li>
          the child elements of <code>select</code> and <code>types</code> are
          lists. List elements are preceded by a dash. This dash must have a
          space after it.
        </li>
      </ul>

      <p>
        For more information about the YAML format, see the{" "}
        <a href="http://yaml.org/spec/1.2/spec.html">YAML specification</a>.
      </p>
    </div>

    <a name="Customise Preset" />
    <h3>Themes</h3>
    <div className="well">
      <p>
        <code>buildings</code>, <code>waterways</code> and{" "}
        <code>hospitals</code> are examples of themes. In formats that have
        layers/tables, one theme will be mapped to one table.
      </p>

      <p>
        Themes are always be the top level keys of the YAML document. Valid
        characters for themes are letters, numbers and underscores.
      </p>
    </div>

    <h3> Geometry Types</h3>
    <div className="well">
      <p>
        the list values under types can be one or more of <code>- points</code>,{" "}
        <code>- lines</code>, <code>- polygons</code>. if the <code>types</code>{" "}
        key is omitted, all 3 geometry types will be included in the theme.
      </p>
    </div>

    <a name="Download" />
    <h3>Column selections</h3>
    <div className="well">
      <p>
        List items under the <code>select</code> key determine the columns for
        each theme.
      </p>
      <pre>select: - name - amenity</pre>
      <p>
        Will populate the <code>name</code> and <code>amenity</code> columns
        with their values from OSM.
      </p>
      Resources for finding information on OSM tagging conventions:
      <ul>
        <li>
          <a href="http://wiki.openstreetmap.org/wiki/Main_Page">
            OpenStreetMap Wiki
          </a>, e.g.{" "}
          <a href="http://wiki.openstreetmap.org/wiki/Key:highway">
            Key:highway
          </a>
        </li>
        <li>
          <a href="https://taginfo.openstreetmap.org">Taginfo</a>, which has
          statistics and maps on OSM keys/values
        </li>
        <li>
          <a href="https://overpass-turbo.eu">Overpass Turbo</a> provides an
          interactive way to query an area for its OSM features and inspect
          their tags.
        </li>
      </ul>
    </div>

    <a name="Upload" />
    <h3>Filters</h3>
    <div className="well">
      <p>
        Filters are under the <code>where:</code> key in each theme. They define
        what subset of OSM features belongs to that theme.
      </p>
      <pre>where: natural IN ('waterway')</pre>
      <p>
        Will filter the theme to only features where the key{" "}
        <code>natural</code> has the value <code>waterway</code>. It is almost
        always necessary to have some kind of filtering, otherwise your theme
        will simply include all OSM features for the given geometry types. You
        can specify a filter using SQL-like syntax. valid SQL keywords are{" "}
        <code>IS NOT NULL, AND, OR, IN, =, !=</code>.
      </p>
      <p>Other examples of filters:</p>
      <pre>
        where: natural = 'waterway' where: 'addr:housenumber' IS NOT NULL where:
        natural IN ('waterway','riverbank')
      </pre>
    </div>
  </div>;
