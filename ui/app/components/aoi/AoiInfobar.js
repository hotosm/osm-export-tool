import PropTypes from "prop-types";
import React, { Component } from "react";

import styles from "../../styles/aoi/AoiInfobar.css";

export const NO_SELECTION_ICON = "warning";
export const POLYGON_ICON = "crop_square";
export const POINT_ICON = "room";

export default class AoiInfobar extends Component {
  static propTypes = {
    aoi: PropTypes.shape({
      description: PropTypes.string,
      geojson: PropTypes.object.isRequired,
      geomType: PropTypes.string,
      title: PropTypes.string
    }),
    zoomToSelection: PropTypes.func
  };

  getGeometryIcon(geomType) {
    switch (geomType) {
      case "Point":
        return POINT_ICON;

      case "Polygon":
        return POLYGON_ICON;

      default:
        return NO_SELECTION_ICON;
    }
  }

  render() {
    const { aoi: { description, geomType, title }, zoomToSelection } = this.props;
    const geometryIcon = this.getGeometryIcon(geomType);

    return (
      <div>
        <div className={styles.aoiInfoWrapper}>
          <div className={styles.aoiInfobar}>
            <div className={styles.topBar}>
              <span className={styles.aoiInfoTitle}>
                <strong>Area Of Interest (AOI)</strong>
              </span>
              <button
                className={styles.activeButton}
                onClick={zoomToSelection}
                type="button"
              >
                <i className={"fa fa-search-plus"} /> ZOOM TO SELECTION
              </button>
            </div>
            <div className={styles.detailBar}>
              <i className={"material-icons " + styles.geometryIcon}>
                {geometryIcon}
              </i>
              <div className={styles.detailText}>
                <div className={styles.aoiTitle}>
                  <strong>
                    {title}
                  </strong>
                </div>
                <div className={styles.aoiDescription}>
                  {description}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }
}
