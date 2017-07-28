import isEqual from "lodash/isEqual";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { MenuItem } from "react-bootstrap-typeahead";

import styles from "../../styles/aoi/TypeaheadMenuItem.css";

export class TypeaheadMenuItem extends Component {
  createDescription = result => {
    const description = [];

    result.adminName2 && description.push(result.adminName2);
    result.adminName1 && description.push(result.adminName1);
    result.countryName && description.push(result.countryName);

    return description.join(", ");
  };

  render() {
    return (
      <MenuItem
        option={this.props.result}
        position={this.props.index}
        className={styles.menuItem}
      >
        <div className={styles.menuItemIconDiv}>
          {this.props.result.bbox && !isEqual(this.props.result.bbox, {})
            ? <i className={"material-icons " + styles.menuItemIcon}>
                crop_din
              </i>
            : <i className={"material-icons " + styles.menuItemIcon}>room</i>}
        </div>
        <div className={styles.menuItemText}>
          <strong>
            {this.props.result.name}
          </strong>
        </div>
        <div className={styles.menuItemText}>
          {this.createDescription(this.props.result)}
        </div>
      </MenuItem>
    );
  }
}

TypeaheadMenuItem.propTypes = {
  result: PropTypes.object,
  index: PropTypes.number
};

export default TypeaheadMenuItem;
