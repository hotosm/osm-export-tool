import { NonIdealState, Spinner } from "@blueprintjs/core";
import React from "react";
import {
  HelpBlock,
  FormControl,
  FormGroup,
  ControlLabel,
  Checkbox
} from "react-bootstrap";
import { FormattedMessage } from "react-intl";
import { connect } from "react-redux";
import Select from "react-select";
import { Field } from "redux-form";
import moment from "moment";
import yaml from "js-yaml";

import { login } from "../actions/meta";
import { selectIsLoggedIn, selectIsLoggingIn } from "../selectors";
import styles from "../styles/utilsStyles.css";

export const AVAILABLE_EXPORT_FORMATS = {
  shp: (
    <span key="shp">
      Shapefile <code>.shp</code>
    </span>
  ),
  geopackage: (
    <span key="geopackage">
      GeoPackage <code>.gpkg</code>
    </span>
  ),
  garmin_img: (
    <span key="garmin_img">
      Garmin <code>.img</code>
    </span>
  ),
  kml: (
    <span key="kml">
      Google Earth <code>.kml</code>
    </span>
  ),
  osm_pbf: (
    <span key="osm_pbf">
      OSM <code>.pbf</code>
    </span>
  ),
  mwm: (
    <span key="mwm">
      MAPS.ME <code>.mwm</code>
    </span>
  ),
  osmand_obf: (
    <span key="osmand_obf">
      OsmAnd <code>.obf</code>
    </span>
  ),
  mbtiles: (
    <span key="osmand_obf">
      MBTiles <code>.mbtiles</code>
    </span>
  ),
  bundle: (
    <span key="bundle">
      <a href="http://posm.io/">POSM</a> bundle
    </span>
  )
};

export const REQUIRES_FEATURE_SELECTION = {
  shp: true,
  geopackage: true,
  garmin_img: true,
  kml: true,
  osm_pbf: true,
  mwm: true,
  osmand_pbf: true
};

export const REQUIRES_TILE_SOURCE = {
  mbtiles: true
};

export const exportFormatNicename = slug => {
  return AVAILABLE_EXPORT_FORMATS[slug];
};

export const formatDate = isodate => {
  return moment(isodate).format("dddd, MMMM Do YYYY, h:mm a");
};

export const formatDuration = seconds => {
  return moment.duration(seconds, "seconds").humanize();
};

export const getFormatCheckboxes = exportFormats =>
  <Field
    name="export_formats"
    component={props => {
      const ks = Object.keys(exportFormats).map((k, i) =>
        <Checkbox
          key={i}
          name={k}
          checked={props.input.value.indexOf(k) !== -1}
          onChange={event => {
            const newValue = [...props.input.value];
            if (event.target.checked) {
              newValue.push(k);
            } else {
              newValue.splice(newValue.indexOf(k), 1);
            }
            return props.input.onChange(newValue);
          }}
        >
          {exportFormats[k]}
        </Checkbox>
      );
      return (
        <div>
          {ks}
        </div>
      );
    }}
  />;

export const renderCheckboxes = ({
  id,
  label,
  input,
  data,
  meta: { error },
  description,
  ...props
}) =>
  <FormGroup controlId={id || input.name} validationState={error && "error"}>
    <ControlLabel>
      {label}
    </ControlLabel>
    {props.children}
    <FormControl.Feedback />
    <HelpBlock>
      {error &&
        <span className={styles.error}>
          {error}
        </span>}
    </HelpBlock>
  </FormGroup>;

export const renderCheckbox = ({ input, data, description, meta, ...props }) =>
  <Checkbox {...input} {...props}>
    {description}
  </Checkbox>;

export const renderInput = ({
  id,
  input,
  label,
  help,
  meta: { error },
  ...props
}) =>
  <FormGroup controlId={id || props.name} validationState={error && "error"}>
    <ControlLabel>
      {label}
    </ControlLabel>
    <FormControl {...input} {...props} />
    <FormControl.Feedback />
    <HelpBlock>
      {error &&
        <p className={styles.error}>
          {error}
        </p>}
      {help}
    </HelpBlock>
  </FormGroup>;

export const renderSelect = ({
  id,
  label,
  input,
  data,
  meta: { error },
  ...props
}) =>
  <FormGroup controlId={id || input.name} validationState={error && "error"}>
    <ControlLabel>
      {label}
    </ControlLabel>
    <FormControl componentClass="select" {...input} {...props} />
    <FormControl.Feedback />
    <HelpBlock>
      {error &&
        <span className={styles.error}>
          {error}
        </span>}
    </HelpBlock>
  </FormGroup>;

export const renderMultiSelect = ({
  id,
  input,
  label,
  help,
  meta: { error },
  ...props
}) =>
  <FormGroup controlId={id || props.name} validationState={error && "error"}>
    <ControlLabel>
      {label}
    </ControlLabel>
    <Select {...input} {...props} onBlur={() => input.onBlur(input.value)} />
    <FormControl.Feedback />
    <HelpBlock>
      {error &&
        <p className={styles.error}>
          {error}
        </p>}
      {help}
    </HelpBlock>
  </FormGroup>;

export const renderTextArea = ({
  id,
  label,
  input,
  data,
  meta: { error },
  ...props
}) =>
  <FormGroup controlId={id || input.name} validationState={error && "error"}>
    <ControlLabel>
      {label}
    </ControlLabel>
    <FormControl componentClass="textarea" {...input} {...props} />
    <FormControl.Feedback />
    <HelpBlock>
      {error &&
        <span className={styles.error}>
          {error}
        </span>}
    </HelpBlock>
  </FormGroup>;

export const slugify = text => {
  const a = "àáäâèéëêìíïîòóöôùúüûñçßÿœæŕśńṕẃǵǹḿǘẍźḧ";
  const b = "aaaaeeeeiiiioooouuuuncsyoarsnpwgnmuxzh";
  const p = new RegExp(a.split("").join("|"), "g");

  return text
    .toString()
    .toLowerCase()
    .replace(/\s+/g, "_") // Replace spaces with -
    .replace(p, c => b.charAt(a.indexOf(c))) // Replace special chars
    .replace(/[^\w_]+/g, "") // Remove all non-word chars
    .replace(/__+/g, "_") // Replace multiple - with single -
    .replace(/^_+/, "") // Trim - from start of text
    .replace(/_+$/, ""); // Trim - from end of text
};

export class PresetParser {
  listForXpath(xpath, root) {
    const a = this.doc.evaluate(
      xpath,
      root,
      this.resolver,
      XPathResult.ORDERED_NODE_ITERATOR_TYPE,
      null
    );
    var r = a.iterateNext();
    const l = [];
    while (r) {
      l.push(r);
      r = a.iterateNext();
    }
    return l;
  }

  resolver() {
    return "http://josm.openstreetmap.de/tagging-preset-1.0";
  }

  collectInputs(itemElem, set) {
    for (var elemType of [
      ".//ns:key",
      ".//ns:text",
      ".//ns:combo",
      ".//ns:multiselect",
      ".//ns:check"
    ]) {
      for (var k of this.listForXpath(elemType, itemElem)) {
        set.add(k.getAttribute("key"));
      }
    }
  }

  constructor(doc) {
    const parser = new DOMParser();
    try {
      this.doc = parser.parseFromString(doc, "text/xml");
    } catch (err) {
      alert(
        "Could not parse XML! Please make sure your JOSM Preset is valid and use the Chrome, Firefox, or Safari browser."
      );
    }
    const collector = {
      points: new Set(),
      lines: new Set(),
      polygons: new Set()
    };
    for (var itemElem of this.listForXpath(".//ns:item", this.doc)) {
      if (!itemElem.getAttribute("type")) {
        continue;
      }
      const types = itemElem.getAttribute("type").split(",");
      if (types.includes("node")) {
        this.collectInputs(itemElem, collector.points);
      }
      if (types.includes("closedway") || types.includes("relation")) {
        // relation?
        this.collectInputs(itemElem, collector.polygons);
      }
      if (types.includes("way")) {
        this.collectInputs(itemElem, collector.lines);
      }
    }

    const fs = {};
    fs.planet_osm_point = {};
    fs.planet_osm_point.types = ["points"];
    fs.planet_osm_point.select = [...collector.points].sort();
    fs.planet_osm_line = {};
    fs.planet_osm_line.types = ["lines"];
    fs.planet_osm_line.select = [...collector.lines].sort();
    fs.planet_osm_polygon = {};
    fs.planet_osm_polygon.types = ["polygons"];
    fs.planet_osm_polygon.select = [...collector.polygons].sort();
    this.featureSelection = fs;
  }

  asYAML() {
    return yaml.safeDump(this.featureSelection);
  }
}

const UNITS = ["B", "kB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"];

export const prettyBytes = num => {
  if (!Number.isFinite(num)) {
    throw new TypeError(`Expected a finite number, got ${typeof num}: ${num}`);
  }

  const neg = num < 0;

  if (neg) {
    num = -num;
  }

  if (num < 1) {
    return (neg ? "-" : "") + num + " B";
  }

  const exponent = Math.min(Math.floor(Math.log10(num) / 3), UNITS.length - 1);
  const numStr = Number((num / Math.pow(1000, exponent)).toPrecision(3));
  const unit = UNITS[exponent];

  return (neg ? "-" : "") + numStr + " " + unit;
};

export const requireAuth = Component =>
  connect(
    state => ({
      isLoggedIn: selectIsLoggedIn(state),
      isLoggingIn: selectIsLoggingIn(state)
    }),
    { login }
  )(
    class extends React.Component {
      componentDidMount() {
        const { isLoggedIn, login } = this.props;

        if (!isLoggedIn) {
          login();
        }
      }

      render() {
        const { isLoggedIn, isLoggingIn, login } = this.props;

        if (isLoggedIn) {
          return <Component {...this.props} />;
        }

        return (
          <NonIdealState
            action={
              <strong>
                <FormattedMessage
                  id="ui.logging_in"
                  defaultMessage="Logging you in..."
                />
              </strong>
            }
            description={
              isLoggingIn ||
              <button type="button" className="btn btn-link" onClick={login}>
                Click here to log in
              </button>
            }
            visual={<Spinner />}
          />
        );
      }
    }
  );
