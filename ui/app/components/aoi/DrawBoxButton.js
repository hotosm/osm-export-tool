import React, { Component } from "react";
import { connect } from "react-redux";

import styles from "../../styles/aoi/DrawAOIToolbar.css";
import {
  setBoxButtonSelected,
  setAllButtonsDefault
} from "../../actions/aoi/mapToolActions";
import { updateMode } from "../../actions/exports";

const DEFAULT_ICON = (
  <div>
    <i className={"material-icons " + styles.defaultButton}>crop_square</i>
    <div className={styles.buttonName}>BOX</div>
  </div>
);

const INACTIVE_ICON = (
  <div>
    <i className={"material-icons " + styles.inactiveButton}>crop_square</i>
    <div className={styles.buttonName + " " + styles.buttonNameInactive}>
      BOX
    </div>
  </div>
);

const SELECTED_ICON = (
  <div>
    <i className={"material-icons " + styles.selectedButton}>clear</i>
    <div className={styles.buttonName}>BOX</div>
  </div>
);

export class DrawBoxButton extends Component {
  state = {
    icon: DEFAULT_ICON
  };

  componentWillReceiveProps(nextProps) {
    const { toolbarIcons: { box } } = this.props;
    const { toolbarIcons: { box: nextBox } } = nextProps;

    if (nextBox !== box) {
      switch (nextBox) {
        case "DEFAULT":
          this.setState({
            icon: DEFAULT_ICON
          });
          break;

        case "INACTIVE":
          this.setState({
            icon: INACTIVE_ICON
          });
          break;

        case "SELECTED":
          this.setState({
            icon: SELECTED_ICON
          });
          break;

        default:
      }
    }
  }

  handleOnClick = () => {
    if (this.state.icon === SELECTED_ICON) {
      this.props.setAllButtonsDefault();
      this.props.handleCancel();
    } else if (this.state.icon === DEFAULT_ICON) {
      this.props.setBoxButtonSelected();
      this.props.updateMode("MODE_DRAW_BBOX");
    }
  };

  render() {
    return (
      <div className={styles.drawButtonGeneral} onClick={this.handleOnClick}>
        {this.state.icon}
      </div>
    );
  }
}

function mapStateToProps(state) {
  return {
    toolbarIcons: state.toolbarIcons,
    mode: state.mode
  };
}

export default connect(mapStateToProps, {
  setAllButtonsDefault,
  setBoxButtonSelected,
  updateMode
})(DrawBoxButton);
