import React, { Component } from "react";

import DropZoneError from "./DropZoneError";
import DropZoneDialog from "./DropZoneDialog";

export default class DropZone extends Component {
  render() {
    return (
      <div>
        <DropZoneDialog />
        <DropZoneError />
      </div>
    );
  }
}
