const fs = require("fs");
var parse = require("csv-parse");
fs.readFile("tagtree.csv", function(err, data) {
  parse(data, { columns: true, trim: true }, function(err, rows) {
    const tagtree = {};
    const taglookup = {};
    for (var row of rows) {

      if (row["Parent"]) {
        taglookup[row["Checkbox Name"]] = {
          geom_types: [],
          keys: [],
          where: row["Condition"]
        }
      } else {
        const category = row["Category"];
        if (!tagtree[category]) tagtree[category] = { children: {} };
        tagtree[category]["children"][row["Checkbox Name"]] = {};
        if (row["additional search terms"]) {
          tagtree[category]["children"][row["Checkbox Name"]].search_terms =
            row["additional search terms"];
        }
        const geom_types = row["Geom Types"].split(",").map(function(x) {
            return x.trim();
          });
        const keys = row["Key Selections (exported when \"Condition\" matches)"].split(",").map(function(x) {
            return x.trim();
          });
        taglookup[row["Checkbox Name"]] = {
          geom_types: geom_types,
          keys: keys,
          where: row["Condition"]
        };

        // add to parent
        for (geom_type of geom_types) {
          if (!taglookup[row["Category"]].geom_types.includes(geom_type)) taglookup[row["Category"]].geom_types.push(geom_type)
        }
        for (key of keys) {
          if (!taglookup[row["Category"]].keys.includes(key)) taglookup[row["Category"]].keys.push(key)
        }
      }
    }
    process.stdout.write("export const TAGTREE = ");
    console.log(JSON.stringify(tagtree, null, 4));
    process.stdout.write("export const TAGLOOKUP = ");
    console.log(JSON.stringify(taglookup, null, 4));
  });
});
