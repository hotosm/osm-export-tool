import React, { Component } from "react";
import styles from "../../styles/aoi/InvalidDrawWarning.css";

export default class InvalidDrawWarning extends Component {
  render() {
    const { msg } = this.props;

    if (msg == null) {
      return null;
    }

    return (
      <div className={styles.invalidWarning}>
        <span>
          {msg}
        </span>
      </div>
    );
  }
}
