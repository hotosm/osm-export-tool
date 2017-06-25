import yaml from 'js-yaml'

export class TreeTag {
  constructor(data) {
    this.data = data
    for (var key in this.data) {
      this.initialize(this.data[key])
    }
  }

  initialize = (node) => {
    node.checked = false
    node.checkbox = true

    if (node.children) {
      node.collapsed = true
      node.indeterminate = false
      for (var key in node.children) {
        this.initialize(node.children[key])
      }
    }
  }

  getNode = (input_path) => {
    const path = input_path.slice() // untested
    var theNode = this.data[path[0]]
    path.shift()
    for (var key of path) {
      theNode = theNode.children[key]
    }
    return theNode
  }

  onTreeNodeCollapseChange = (path) => {
    const node = this.getNode(path)
    node.collapsed = !node.collapsed
  }

  setChecked = (node,bool) => {
    node.checked = bool
    for(var key in node.children) {
      this.setChecked(node.children[key],bool)
    }
  }

  allChecked = (node) => {
    // this can be short-circuited?
    var retval = true
    if (node.children) {
      for (var key in node.children) {
        retval = retval && this.allChecked(node.children[key])
      }
    }
    return retval && node.checked
  }

  noneChecked = (node) => {
    // this can be short-circuited?
    var retval = true
    if (node.children) {
      for (var key in node.children) {
        retval = retval && this.noneChecked(node.children[key])
      }
    }
    return retval && !node.checked
  }

  setParents = (path) => {
    const node = this.getNode(path)
    var numTrue = 0
    var numChildren = 0
    for (var key in node.children) {
      if (node.children[key].checked) numTrue++
      numChildren++
    }
    if (numTrue === numChildren) {
      node.checked = true
      node.indeterminate = false
    } else if (numTrue === 0) {
      node.checked = false
      node.indeterminate = false
    } else {
      node.checked = true // semantics; indeterminate = true
      node.indeterminate = true
    }
  }

  onTreeNodeCheckChange = (path) => {
    const node = this.getNode(path)
    if (node.children) {
      node.indeterminate = false // untested
      if (this.allChecked(node)) {
        this.setChecked(node,false)
      } else {
        this.setChecked(node,true)
      }

    } else {
      // it's a leaf node.
      node.checked = !node.checked
    }

    // the clicked node and its children's state are determined.
    // now each parent of the clicked node needs to have its 
    // check/indeterminate state set correctly,
    // starting from bottom up.
    path.pop() //untested (for 2+ depth)
    while (path.length > 0) {
      this.setParents(path)
      path.pop()
    }
  }

  checkedValues = () => {
    var retval = []
    for (var key in this.data) {
      retval = retval.concat(this.checkedSubtree(this.data[key],key))
    }
    return retval
  }

  checkedSubtree = (node,key) => {
    if (node.children) {
      var retval = []
      for (var childKey in node.children) {
        retval = retval.concat(this.checkedSubtree(node.children[childKey],childKey))
      }
      return retval
    } else {
      if (node.checked) {
        return [key]
      }
      return []
    }
  }

  visibleData = (query) => {
    // given a search string, return filtered tree, uncollapsing the path to results
    if (query) {
      const retval = {}
      for (var key in this.data) {
        const subtree = this.visibleSubtree(this.data[key],key,query)
        if (subtree) {
          retval[key] = subtree
        }
      }
      return retval
    }
    return this.data
  }

  visibleSubtree = (node,key,query) => {
    const retval = {}
    retval.children = {}
    var found = false
    if (node.children) {
      for (var childKey in node.children) {
        const subtree = this.visibleSubtree(node.children[childKey], childKey, query)
        if (subtree) {
          retval.children[childKey] = subtree
          found = true
        }
      }
    }
    retval.collapsed = false
    retval.checked = node.checked
    retval.indeterminate = node.indeterminate
    retval.checkbox = true
    if (found || key.includes(query)) {
      return retval
    }
    return false
  }

  labelFilter = (label) => {
    // do localization here
    return label[0].toUpperCase() + label.substring(1);
  }
}

// consumes a list of checkbox names and outputs a YAML feature selection.
export class TreeTagYAML {
  createPropIfNeeded = (table_name,geom_type) => {
    if (this.data[table_name]) return
    this.data[table_name] = {
      types:[geom_type],
      select:new Set(),
      where:[]
    }
  }

  constructor(lookup,checkbox_list) {
    this.data = {}
    for (var name of checkbox_list) {
      for(var geom_type of lookup[name].geom_types) {
        const t = "planet_osm_" + geom_type
        this.createPropIfNeeded(t,geom_type + "s")
        for (var key of lookup[name].keys) {
          this.data[t].select.add(key)
        }
        if (lookup[name].where) {
          this.data[t].where.push(lookup[name].where)
        }
      }
    }

  }

  dataAsObj = () => {
    const retval = {}
    for(var tname in this.data) {
      retval[tname] = {
        'types':this.data[tname].types,
        'select':[...this.data[tname].select].sort(),
        'where':this.data[tname].where
      }
    }
    return retval
  }

  dataAsYaml = () => {
    return yaml.safeDump(this.dataAsObj(),{lineWidth:-1,noCompatMode:true})
  }
}
