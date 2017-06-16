import React from 'react';
import { HelpBlock, FormControl, FormGroup, ControlLabel, Checkbox } from 'react-bootstrap';
import { Field } from 'redux-form'
import Select from 'react-select';
import styles from '../styles/utilsStyles.css'
import yaml from 'js-yaml';

export const AVAILABLE_EXPORT_FORMATS = {
  shp: 'ESRI Shapefiles',
  geopackage: 'GeoPackage',
  garmin_img: 'Garmin .IMG',
  kml: 'Google Earth .KMZ',
  xml: 'OSM .XML',
  pbf: 'OSM .PBF'
};

export const getFormatCheckboxes = (export_formats) =>
    <Field
      name="export_formats"
      component={(props) => {
        const ks = Object.keys(export_formats).map((k, i) =>
          <Checkbox
          key={i}
          name={k}
          checked={props.input.value.indexOf(k) !== -1}
          onChange={event => {
            const newValue = [...props.input.value];
            if(event.target.checked) {
              newValue.push(k);
            } else {
              newValue.splice(newValue.indexOf(k), 1);
            }
            return props.input.onChange(newValue);
          }}>
          {export_formats[k]}
          </Checkbox>
        );
        return <div>{ks}</div>
      }}/>

export const renderCheckboxes = ({id, label, input, data, meta: { error }, description, ...props}) =>
  <FormGroup controlId={id || input.name} validationState={error && 'error'}>
    <ControlLabel>{label}</ControlLabel>
    {props.children}
    <FormControl.Feedback />
    <HelpBlock>{error && <span className={styles.error}>{error}</span>}</HelpBlock>
  </FormGroup>;

export const renderCheckbox = ({input, data, description, meta, ...props}) =>
  <Checkbox {...input} {...props}>{description}</Checkbox>;

export const renderInput = ({ id, input, label, help, meta: { error }, ...props }) =>
  <FormGroup controlId={id || props.name} validationState={error && 'error'}>
    <ControlLabel>{label}</ControlLabel>
    <FormControl {...input} {...props} />
    <FormControl.Feedback />
    <HelpBlock>{error && <p className={styles.error}>{error}</p>}{help}</HelpBlock>
  </FormGroup>;

export const renderSelect = ({id, label, input, data, meta: { error }, ...props}) =>
  <FormGroup controlId={id || input.name} validationState={error && 'error'}>
    <ControlLabel>{label}</ControlLabel>
    <FormControl componentClass='select' {...input} {...props} />
    <FormControl.Feedback />
    <HelpBlock>{error && <span className={styles.error}>{error}</span>}</HelpBlock>
  </FormGroup>;

export const renderMultiSelect = ({ id, input, label, help, meta: { error }, ...props }) =>
  <FormGroup controlId={id || props.name} validationState={error && 'error'}>
    <ControlLabel>{label}</ControlLabel>
    <Select
      {...input}
      {...props}
      onBlur={() => input.onBlur(input.value)}
    />
    <FormControl.Feedback />
    <HelpBlock>{error && <p className={styles.error}>{error}</p>}{help}</HelpBlock>
  </FormGroup>;

export const renderTextArea = ({id, label, input, data, meta: { error }, ...props}) =>
  <FormGroup controlId={id || input.name} validationState={error && 'error'}>
    <ControlLabel>{label}</ControlLabel>
    <FormControl componentClass='textarea' {...input} {...props} />
    <FormControl.Feedback />
    <HelpBlock>{error && <span className={styles.error}>{error}</span>}</HelpBlock>
  </FormGroup>;

export const slugify = (text) => {
  const a = 'àáäâèéëêìíïîòóöôùúüûñçßÿœæŕśńṕẃǵǹḿǘẍźḧ'
  const b = 'aaaaeeeeiiiioooouuuuncsyoarsnpwgnmuxzh'
  const p = new RegExp(a.split('').join('|'), 'g')

  return text.toString().toLowerCase()
    .replace(/\s+/g, '_')           // Replace spaces with -
    .replace(p, c =>
        b.charAt(a.indexOf(c)))     // Replace special chars
    .replace(/[^\w_]+/g, '')       // Remove all non-word chars
    .replace(/\_\_+/g, '_')         // Replace multiple - with single -
    .replace(/^_+/, '')             // Trim - from start of text
    .replace(/_+$/, '')             // Trim - from end of text
}


export class PresetParser {
  listForXpath(xpath,root) {
    const a = this.doc.evaluate(xpath,root,this.resolver,XPathResult.ORDERED_NODE_ITERATOR_TYPE)
    var r = a.iterateNext()
    const l = []
    while(r) {
      l.push(r)
      r = a.iterateNext()
    }
    return l
  }

  resolver() {
    return "http://josm.openstreetmap.de/tagging-preset-1.0"
  }

  collectInputs(itemElem,set) {
    for (var elemType of [".//ns:key",".//ns:text",".//ns:combo",".//ns:multiselect",".//ns:check"]) {
      for (var k of this.listForXpath(elemType,itemElem)) {
        set.add(k.getAttribute('key')) 
      }
    }
  }

  constructor(doc) {
    const parser = new DOMParser()
    this.doc = parser.parseFromString(doc, "text/xml");
    const collector = {
      points:new Set(),
      lines:new Set(),
      polygons:new Set()
    }
    for (var itemElem of this.listForXpath(".//ns:item",this.doc)) {
      const types = itemElem.getAttribute("type").split(',')
      if (types.includes("node")) {
        this.collectInputs(itemElem,collector.points)
      }
      if (types.includes("closedway") || types.includes("relation")) { // relation?
        this.collectInputs(itemElem,collector.polygons)
      }
      if (types.includes("way")) {
        this.collectInputs(itemElem,collector.lines)
      }
    }

    const fs = {}
    fs.planet_osm_point = {}
    fs.planet_osm_point.geom_types = ["points"]
    fs.planet_osm_point.select = [...collector.points].sort()
    fs.planet_osm_line = {}
    fs.planet_osm_line.geom_types = ["lines"]
    fs.planet_osm_line.select = [...collector.lines].sort()
    fs.planet_osm_polygon = {}
    fs.planet_osm_polygon.geom_types = ["polygons"]
    fs.planet_osm_polygon.select = [...collector.polygons].sort()
    this.featureSelection = fs
  }

  as_yaml() {
    return yaml.safeDump(this.featureSelection)
  }
  
}
