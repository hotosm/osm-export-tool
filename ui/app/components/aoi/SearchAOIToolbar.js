import PropTypes from "prop-types";
import React, { Component } from "react";
import { connect } from "react-redux";
import styles from "../../styles/aoi/SearchAOIToolbar.css";
import { Typeahead, Menu } from "react-bootstrap-typeahead";
import { getGeonames } from "../../actions/aoi/searchToolbarActions";
import { TypeaheadMenuItem } from "./TypeaheadMenuItem";
import SearchAOIButton from "./SearchAOIButton";
import {
  setSearchAOIButtonSelected,
  setAllButtonsDefault
} from "../../actions/aoi/mapToolActions";

const debounce = require("lodash/debounce");

export class SearchAOIToolbar extends Component {
  constructor(props) {
    super(props);

    this.handleChange = this.handleChange.bind(this);
    this.handleEnter = this.handleEnter.bind(this);

    this.state = {
      value: "",
      suggestions: []
    };
  }

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

  handleChange(e) {
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
    // If 2 or more characters are entered then make request for suggested names.
    if (e.length >= 2) {
      this.props.getGeonames(e);
    } else {
      // If one or zero characters are entered then dont provide suggestions
      // If there are suggestions remove them
      if (this.state.suggestions.length > 0) {
        this.setState({ suggestions: [] });
      }
    }
  }

  handleEnter(e) {
    this.setState({ suggestions: [] });
    if (e.length > 0) {
      this.props.setSearchAOIButtonSelected();
      this.props.handleSearch(e[0]);
      this.refs.typeahead.getInstance().blur();
    }
  }

  render() {
    return (
      <div className={styles.searchbarDiv}>
        <div className={styles.typeahead}>
          <Typeahead
            ref="typeahead"
            disabled={this.props.toolbarIcons.search === "INACTIVE"}
            options={this.state.suggestions}
            onChange={this.handleEnter}
            placeholder={
              "Search for a location or enter minX,minY,maxX,maxY"
            }
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
  handleSearch: PropTypes.func,
  handleCancel: PropTypes.func,
  setSearchAOIButtonSelected: PropTypes.func
};

function mapStateToProps(state) {
  return {
    geonames: state.geonames,
    toolbarIcons: state.toolbarIcons
  };
}

function mapDispatchToProps(dispatch) {
  return {
    getGeonames: query => {
      dispatch(getGeonames(query));
    },
    setAllButtonsDefault: () => {
      dispatch(setAllButtonsDefault());
    },
    setSearchAOIButtonSelected: () => {
      dispatch(setSearchAOIButtonSelected());
    }
  };
}

export default connect(mapStateToProps, mapDispatchToProps)(SearchAOIToolbar);
