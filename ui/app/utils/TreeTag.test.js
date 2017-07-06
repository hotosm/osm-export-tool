var clonedeep = require("lodash/clonedeep");
import { TreeTag, TreeTagYAML } from "./TreeTag";

const TEST_DATA = {
  buildings: {
    children: {
      schools: {
        children: {
          highschools: {}
        }
      },
      libraries: {}
    }
  },
  transportation: {}
};

test("initialization of data structure", () => {
  const t = new TreeTag(clonedeep(TEST_DATA));
  const v = t.visibleData();
  expect(v.buildings.checked).toBe(false);
  expect(v.buildings.checkbox).toBe(true);
  expect(v.buildings.children.schools.checked).toBe(false);
  expect(v.buildings.children.schools.checkbox).toBe(true);

  // a node with children has collapsed/indeterminate
  expect(v.buildings.collapsed).toBe(true);
  expect(v.buildings.indeterminate).toBe(false);
  expect(v.transportation.collapsed).toBeUndefined();
  expect(v.transportation.indeterminate).toBeUndefined();
});

test("setting collapsed/uncollapsed", () => {
  const t = new TreeTag(clonedeep(TEST_DATA));
  t.onTreeNodeCollapseChange(["buildings", "schools"]);
  const v = t.visibleData();
  expect(v.buildings.children.schools.collapsed).toBe(false);
});

test("(Logic) if less than all children checked, setting checked checks all children", () => {
  const t = new TreeTag(clonedeep(TEST_DATA));
  t.onTreeNodeCheckChange(["buildings", "schools"]);
  t.onTreeNodeCheckChange(["buildings"]);
  const v = t.visibleData();
  expect(v.buildings.checked).toBe(true);
  expect(v.buildings.children.schools.checked).toBe(true);
  expect(v.buildings.children.libraries.checked).toBe(true);
});

test("(Logic) if all children checked, setting checked unchecks all children", () => {
  const t = new TreeTag(clonedeep(TEST_DATA));
  t.onTreeNodeCheckChange(["buildings", "schools"]);
  t.onTreeNodeCheckChange(["buildings", "libraries"]);
  t.onTreeNodeCheckChange(["buildings"]);
  const v = t.visibleData();
  expect(v.buildings.checked).toBe(false);
  expect(v.buildings.children.schools.checked).toBe(false);
  expect(v.buildings.children.libraries.checked).toBe(false);
});

test("(UI) setting checked sets checked/indeterminate states of parents", () => {
  const t = new TreeTag(clonedeep(TEST_DATA));
  t.onTreeNodeCheckChange(["buildings", "schools"]);
  const v = t.visibleData();
  expect(v.buildings.children.schools.checked).toBe(true);
  expect(v.buildings.indeterminate).toBe(true);
});

test("(UI) setting checked doesnt set parent indeterminate state if all checked", () => {
  const t = new TreeTag(clonedeep(TEST_DATA));
  t.onTreeNodeCheckChange(["buildings", "schools"]);
  t.onTreeNodeCheckChange(["buildings", "libraries"]);
  const v = t.visibleData();
  expect(v.buildings.indeterminate).toBe(false);
  expect(v.buildings.checked).toBe(true);
});

test("filtering to search values uncollapses parents", () => {
  const t = new TreeTag(clonedeep(TEST_DATA));
  const v = t.visibleData("high");
  expect(v.transportation).toBeUndefined();
  expect(v.buildings.children.libraries).toBeUndefined();
  expect(v.buildings.collapsed).toBe(false);
  expect(v.buildings.children.schools.collapsed).toBe(false);
});

const SEARCHABLE_DATA = {
  buildings: {},
  transportation: {
    search_terms: "transit"
  }
};

test("filtering uses additional search terms", () => {
  const t = new TreeTag(clonedeep(SEARCHABLE_DATA));
  const v = t.visibleData("transit");
  expect(v.transportation).toBeDefined();
});

test("getting flattened list of checked values", () => {
  const t = new TreeTag(clonedeep(TEST_DATA));
  t.onTreeNodeCheckChange(["buildings", "schools"]);
  t.onTreeNodeCheckChange(["buildings", "libraries"]);
  const c = t.checkedValues();
  expect(c).toEqual(["highschools", "libraries"]);
});

const TEST_LOOKUP = {
  libraries: {
    geom_types: ["polygon"],
    keys: ["name", "amenity"],
    where: "amenity='library'"
  }
};

test("converts list of checkboxes to YAML", () => {
  const y = new TreeTagYAML(TEST_LOOKUP, ["libraries"]).dataAsObj();
  expect(y.planet_osm_line).toBeUndefined();
  expect(y.planet_osm_polygon.select[0]).toEqual("amenity");
  expect(y.planet_osm_polygon.select[1]).toEqual("name");
});
