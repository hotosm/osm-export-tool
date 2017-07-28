import React, { Component } from "react";
import { connect } from "react-redux";

import styles from "../../styles/aoi/DrawAOIToolbar.css";
import {
  setFreeButtonSelected,
  setAllButtonsDefault
} from "../../actions/aoi/mapToolActions";
import { updateMode } from "../../actions/exports";

const DEFAULT_ICON = (
  <div>
    <i className={"material-icons " + styles.defaultButton}>create</i>
    <div className={styles.buttonName}>DRAW</div>
  </div>
);

const INACTIVE_ICON = (
  <div>
    <i className={"material-icons " + styles.inactiveButton}>create</i>
    <div className={styles.buttonName + " " + styles.buttonNameInactive}>
      DRAW
    </div>
  </div>
);

const SELECTED_ICON = (
  <div>
    <i className={"material-icons " + styles.selectedButton}>clear</i>
    <div className={styles.buttonName}>DRAW</div>
  </div>
);

export class DrawFreeButton extends Component {
  constructor(props) {
    super(props);
    this.handleOnClick = this.handleOnClick.bind(this);
    this.state = {
      icon: DEFAULT_ICON
    };
  }

  componentWillReceiveProps(nextProps) {
    const { toolbarIcons: { draw } } = this.props;
    const { toolbarIcons: { draw: nextDraw } } = nextProps;

    if (nextDraw !== draw) {
      switch (nextDraw) {
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
      this.props.setFreeButtonSelected();
      this.props.updateMode("MODE_DRAW_FREE");
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
  setFreeButtonSelected,
  updateMode
})(DrawFreeButton);
