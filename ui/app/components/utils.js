import React from 'react';
import { HelpBlock, FormControl, FormGroup, ControlLabel, Checkbox } from 'react-bootstrap';
import { Field } from 'redux-form'
import Select from 'react-select';
import styles from '../styles/utilsStyles.css'
import * as urlify from 'urlify';
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

const urlize = urlify.create()

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

  themes() {
    // find the first level of "group" that has more than one element.
    var path = "/ns:presets/ns:group"
    var l = this.listForXpath(path,this.doc)
    var depth = 0
    while (l.length === 1) {
      depth = depth + 1
      l = this.listForXpath(path + "/ns:group".repeat(depth),this.doc)
    }
    if (l.length === 0) {
      // if all group depths are 1, just return the deepest
      if (depth === 0) return []
      else return this.listForXpath(path+"/ns:group".repeat(depth-1),this.doc)
    }
    return l
  }

  geomTypesForTheme(themeElem) {
      console.log(themeElem)
      const l = new Set()
      for (var i of this.listForXpath(".//ns:item",themeElem)) {
        const types = i.getAttribute("type").split(',')
        if (types.includes("node")) l.add("points")
        if (types.includes("closedway")) l.add("polygons")
        if (types.includes("way")) l.add("lines")
        if (types.includes("relation")) l.add("polygons") // this is questionable
      }
      return l
  }

  keysForTheme(themeElem) {
      const l = new Set()
      for (var i of this.listForXpath(".//ns:key",themeElem)) {
        l.add(i.getAttribute("key"))
      }
      return l
  }

  whereForTheme(themeElem) {
      var l = []
      for (var i of this.listForXpath(".//ns:key",themeElem)) {
        if (i.getAttribute("value")) {
          l.push(i.getAttribute("key") + "=" + '"' + i.getAttribute("value") + '"')
        } else {
          l.push(i.getAttribute("key") + " IS NOT NULL")
        }
      }

      return l.join(' OR ')
  }

  constructor(doc) {
    const parser = new DOMParser();
    this.doc = parser.parseFromString(doc, "text/xml");
    this.featureSelection = {}
    for (var themeElem of this.themes()) {
      const themeName = urlize(themeElem.getAttribute('name'))
      this.featureSelection[themeName] = {}
      this.featureSelection[themeName].geom_types = [...this.geomTypesForTheme(themeElem)]
      this.featureSelection[themeName].select = [...this.keysForTheme(themeElem)]
      this.featureSelection[themeName].where = this.whereForTheme(themeElem)
    }
  }

  as_yaml() {
    return yaml.safeDump(this.featureSelection)
  }
  
}
