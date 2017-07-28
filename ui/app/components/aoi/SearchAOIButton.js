import PropTypes from "prop-types";
import React, { Component } from "react";
import { connect } from "react-redux";

import styles from "../../styles/aoi/SearchAOIButton.css";
import {
  setSearchAOIButtonSelected,
  setAllButtonsDefault
} from "../../actions/aoi/mapToolActions";

const DEFAULT_ICON = (
  <div>
    <i className={"material-icons " + styles.defaultButton}>search</i>
    <div className={styles.buttonName}>SEARCH</div>
  </div>
);

const INACTIVE_ICON = (
  <div>
    <i className={"material-icons " + styles.inactiveButton}>search</i>
    <div className={styles.buttonName + " " + styles.buttonNameInactive}>
      SEARCH
    </div>
  </div>
);

const SELECTED_ICON = (
  <div>
    <i className={"material-icons " + styles.selectedButton}>clear</i>
    <div className={styles.buttonName}>SEARCH</div>
  </div>
);

export class SearchAOIButton extends Component {
  state = {
    icon: DEFAULT_ICON
  };

  componentWillReceiveProps(nextProps) {
    // TODO state is wholely unnecessary
    if (nextProps.toolbarIcons.search !== this.props.toolbarIcons.search) {
      // If the button has been selected update the button state
      if (nextProps.toolbarIcons.search === "SELECTED") {
        this.setState({ icon: SELECTED_ICON });
      }
      // If the button has been de-selected update the button state
      if (nextProps.toolbarIcons.search === "DEFAULT") {
        this.setState({ icon: DEFAULT_ICON });
      }
      // If the button has been set as inactive update the state
      if (nextProps.toolbarIcons.search === "INACTIVE") {
        this.setState({ icon: INACTIVE_ICON });
      }
    }
  }

  handleOnClick = () => {
    if (this.state.icon === SELECTED_ICON) {
      this.props.handleCancel();
      this.props.setAllButtonsDefault();
    }
  };

  render() {
    return (
      <div className={styles.buttonGeneral} onClick={this.handleOnClick}>
        {this.state.icon}
      </div>
    );
  }
}

SearchAOIButton.propTypes = {
  toolbarIcons: PropTypes.object,
  handleCancel: PropTypes.func,
  setSearchAOIButtonSelected: PropTypes.func,
  setAllButtonsDefault: PropTypes.func
};

function mapStateToProps(state) {
  return {
    toolbarIcons: state.toolbarIcons
  };
}

export default connect(mapStateToProps, {
  setAllButtonsDefault,
  setSearchAOIButtonSelected
})(SearchAOIButton);
