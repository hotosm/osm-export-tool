import React from "react";
import { Panel } from "react-bootstrap";

import { TAGLOOKUP } from "../utils/TreeTagSettings";

export default props => {
  if (!props.name) {
    return <Panel>Hover over a checkbox to see its definition.</Panel>;
  } else {
    return (
      <Panel>
        <strong>{props.name}</strong>
        <br />
        <strong>Geometry types:</strong>{" "}
        {TAGLOOKUP[props.name]["geom_types"].join(", ")}
        <br />
        <strong>Keys:</strong>
        <ul>
          {TAGLOOKUP[props.name]["keys"].map((o, i) => {
            return (
              <li key={i}>
                {o}
              </li>
            );
          })}
        </ul>
        <strong>Where:</strong> {TAGLOOKUP[props.name]["where"]}
      </Panel>
    );
  }
};
