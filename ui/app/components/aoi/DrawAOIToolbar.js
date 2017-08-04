import React, { Component } from "react";
import { FormattedMessage } from "react-intl";
import { connect } from "react-redux";

import styles from "../../styles/aoi/DrawAOIToolbar.css";
import DrawBoxButton from "./DrawBoxButton";
import DrawFreeButton from "./DrawFreeButton";
import MapViewButton from "./MapViewButton";
import ImportButton from "./ImportButton";
import { setAllButtonsDefault } from "../../actions/aoi/mapToolActions";

export class DrawAOIToolbar extends Component {
  componentDidMount() {
    this.props.setAllButtonsDefault();
  }

  render() {
    const { handleCancel, setMapView } = this.props;

    return (
      <div>
        <div className={styles.drawButtonsContainer}>
          <div className={styles.drawButtonsTitle}>
            <strong>
              <FormattedMessage
                id="ui.aoi_toolbar.tools"
                defaultMessage="Tools"
              />
            </strong>
          </div>
          <DrawBoxButton handleCancel={handleCancel} />
          <DrawFreeButton handleCancel={handleCancel} />
          <MapViewButton handleCancel={handleCancel} setMapView={setMapView} />
          <ImportButton handleCancel={handleCancel} />
        </div>
      </div>
    );
  }
}

export default connect(null, { setAllButtonsDefault })(DrawAOIToolbar);
