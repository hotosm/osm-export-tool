const fs = require("fs");
var parse = require("csv-parse");
fs.readFile("tagtree.csv", function(err, data) {
  parse(data, { columns: true, trim: true }, function(err, rows) {
    const tagtree = {};
    const taglookup = {};
    for (var row of rows) {
      const category = row["Category"];
      if (!tagtree[category]) tagtree[category] = { children: {} };
      tagtree[category]["children"][row["Checkbox Name"]] = {};
      if (row["additional search terms"]) {
        tagtree[category]["children"][row["Checkbox Name"]].search_terms =
          row["additional search terms"];
      }
      taglookup[row["Checkbox Name"]] = {
        geom_types: row["Geom Types"].split(",").map(function(x) {
          return x.trim();
        }),
        keys: row["Key Selections (exported when \"Condition\" matches)"].split(",").map(function(x) {
          return x.trim();
        }),
        where: row["Condition"]
      };
    }
    console.log("export const TAGTREE = \\");
    console.log(JSON.stringify(tagtree, null, 4));
    console.log("export const TAGLOOKUP = \\");
    console.log(JSON.stringify(taglookup, null, 4));
  });
});
