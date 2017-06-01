import React, {Component} from 'react';
import { FormGroup, FormControl, Button } from 'react-bootstrap';
import * as urlify from 'urlify';
import yaml from 'js-yaml';

const urlize = urlify.create()

class PresetParser {
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
    var depth = 1
    while (l.length === 1) {
      path = path + "/ns:group"  
      l = this.listForXpath(path,this.doc)
    }
    if (l.length === 0) {
      if (depth === 1) return null
      // if all group depths are 1, just return the top level
      return this.listForXpath("/ns:presets/ns:group")
    }
    return l
  }

  geomTypesForTheme(themeElem) {
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
        l.push(i.getAttribute("key") + "=" + i.getAttribute("value"))
      }

      return l.join(' OR ')
  }

  constructor(doc) {
    const parser = new DOMParser();
    this.doc = parser.parseFromString(doc, "text/xml");
    this.featureSelection = {}
    console.log(this.themes())
    for (var themeElem of this.themes()) {
      const themeName = urlize(themeElem.getAttribute('name'))
      this.featureSelection[themeName] = {}
      this.featureSelection[themeName].geom_types = [...this.geomTypesForTheme(themeElem)]
      this.featureSelection[themeName].keys = [...this.keysForTheme(themeElem)]
      this.featureSelection[themeName].where = this.whereForTheme(themeElem)
    }
  }

  as_yaml() {
    return yaml.safeDump(this.featureSelection)
  }
  
}


export class PresetToYaml extends Component {
    constructor(props) {
        super(props);
        this.state = {value:""}
    }

    handleConvert(event) {
        const p = new PresetParser(this.state.value)
        this.setState({yaml:p.as_yaml()})
    }

    handleChange(event) {
      this.setState({value: event.target.value});
    }

    render() {
      return( 
        <div>
        <FormGroup>
        <FormControl rows="10" onChange={this.handleChange.bind(this)} componentClass="textarea"/>
        </FormGroup>
         <Button
           bsStyle='primary'
           onClick={this.handleConvert.bind(this)}
         >
         Convert Preset
         </Button>
        <pre>
          {this.state.yaml}
        </pre>

        </div>)
    }
}

export default PresetToYaml;

