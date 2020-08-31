import debounce from "lodash/debounce";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { connect } from "react-redux";

import styles from "../../styles/aoi/SearchAOIToolbar.css";
import { Typeahead, Menu } from "react-bootstrap-typeahead";
import { getGeonames, getNominatim } from "../../actions/aoi/searchToolbarActions";
import { TypeaheadMenuItem } from "./TypeaheadMenuItem";
import SearchAOIButton from "./SearchAOIButton";
import {
  setSearchAOIButtonSelected,
  setAllButtonsDefault
} from "../../actions/aoi/mapToolActions";
import { NonIdealState, Spinner } from "@blueprintjs/core";

const getCountryISO2 = require("country-iso-3-to-2");
const isoCountriesLanguages = require("@hotosm/iso-countries-languages");

export class SearchAOIToolbar extends Component {
  state = {
    value: "",
    suggestions: [],
    loading: false,
  };

  componentWillMount() {
    this.debouncer = debounce(e => {
      this.handleChange(e);
    }, 500);
  }

  componentWillReceiveProps(nextProps) {
    if (nextProps.geonames.fetched) {
      this.setState({ suggestions: nextProps.geonames.geonames });
    } else {
      if (this.state.suggestions.length > 0) {
        this.setState({ suggestions: [] });
      }
    }
    if (nextProps.toolbarIcons.search !== this.props.toolbarIcons.search) {
      if (nextProps.toolbarIcons.search === "DEFAULT") {
        this.refs.typeahead.getInstance().clear();
      }
    }
  }

  handleChange = e => {
    // if it matches minx,miny,maxx,maxy
    const match = e.split(",").map(Number);
    if (match.length === 4 && match[0] < match[2] && match[1] < match[3]) {
      this.props.setSearchAOIButtonSelected();
      this.props.handleSearch({
        name: "Manually Entered Bounds",
        bbox: {
          west: match[0],
          south: match[1],
          east: match[2],
          north: match[3]
        }
      });
    }
    const matchISO3 = e.split(":")
    if (matchISO3.length === 2 && matchISO3[0] === "code" && matchISO3[1].length === 3) {
      const [_, iso3] = matchISO3;
      this.setState(p => {
        return {...p, loading: true}
      })

      // Get iso2 from iso3.
      const iso2 = getCountryISO2(iso3.toUpperCase());

      // Get country name from iso2.
      const country = isoCountriesLanguages.getCountry("en", iso2);
      const params = {
        country: country,
        countryCode: iso2
      };
      this.props.getNominatim(params).then(r => {
        this.props.handleSearchNominatim({
          geojson: r,
          name: country,
          description: "Nominatim polygon",
        });
      })
      .finally(() => {
        this.setState(p => {
          return {...p, loading: false}
        });
      });
    } else if (e.length >= 2) {
      // If 2 or more characters are entered then make request for suggested names.
      this.props.getGeonames(e);
    } else {
      // If one or zero characters are entered then dont provide suggestions
      // If there are suggestions remove them
      if (this.state.suggestions.length > 0) {
        this.setState({ suggestions: [] });
      }
    }
  };

  handleEnter = e => {
    this.setState({ suggestions: [] });
    if (e.length > 0) {
      this.props.setSearchAOIButtonSelected();
      this.props.handleSearch(e[0]);
      this.refs.typeahead.getInstance().blur();
    }
  };

  render() {
    return (
      <div className={styles.searchbarDiv}>
        <div className={styles.loadingSpinner}>
          {this.state.loading === true ? <Spinner className={styles.spinnerClass}/>  : null}
        </div>
        <div className={styles.typeahead}>
          <Typeahead
            ref="typeahead"
            disabled={this.props.toolbarIcons.search === "INACTIVE"}
            options={this.state.suggestions}
            onChange={this.handleEnter}
            placeholder={"Search for a location or enter a bounding box as 'minX, minY, maxX, maxY'"}
            onInputChange={this.debouncer}
            labelKey={"name"}
            paginate={false}
            emptyLabel={""}
            minLength={2}
            renderMenu={(results, menuProps) => {
              return (
                <Menu {...menuProps}>
                  {results.map((result, index) =>
                    <TypeaheadMenuItem
                      result={result}
                      index={index}
                      key={index}
                    />
                  )}
                </Menu>
              );
            }}
          />
        </div>
        <div className={styles.searchAOIButtonContainer}>
          <SearchAOIButton handleCancel={this.props.handleCancel} />
        </div>
      </div>
    );
  }
}

SearchAOIToolbar.propTypes = {
  toolbarIcons: PropTypes.object,
  geonames: PropTypes.object,
  getGeonames: PropTypes.func,
  getNominatim: PropTypes.func,
  handleSearch: PropTypes.func,
  handleSearchNominatim: PropTypes.func,
  handleCancel: PropTypes.func,
  setSearchAOIButtonSelected: PropTypes.func
};

function mapStateToProps(state) {
  return {
    geonames: state.geonames,
    toolbarIcons: state.toolbarIcons
  };
}

export default connect(mapStateToProps, {
  getGeonames,
  getNominatim,
  setAllButtonsDefault,
  setSearchAOIButtonSelected
})(SearchAOIToolbar);
