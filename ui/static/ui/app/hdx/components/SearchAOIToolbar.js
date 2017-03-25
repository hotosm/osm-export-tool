import React, {Component} from 'react';
import {connect} from 'react-redux';
import styles from '../styles/SearchAOIToolbar.css';
import {Typeahead, Menu, MenuItem} from 'react-bootstrap-typeahead';
import {getGeonames} from '../actions/searchToolbarActions';
import {TypeaheadMenuItem} from './TypeaheadMenuItem';
import SearchAOIButton from './SearchAOIButton';
import {setSearchAOIButtonSelected, setAllButtonsDefault} from '../actions/mapToolActions';

const debounce = require('lodash/debounce');

export class SearchAOIToolbar extends Component {

    constructor(props) {
        super(props)

        this.handleChange = this.handleChange.bind(this);
        this.handleEnter = this.handleEnter.bind(this);

        this.state = {
            value: '',
            suggestions: [],
        }
    }

    componentWillMount() {
      this.debouncer = debounce(e => {
        this.handleChange(e);
      }, 500);
    }

    componentWillReceiveProps(nextProps) {
        if(nextProps.geonames.fetched == true) {
            this.setState({suggestions: nextProps.geonames.geonames});
        }
        else {
            if(this.state.suggestions.length > 0) {
                this.setState({suggestions: []});
            }
        }
        if(nextProps.toolbarIcons.search != this.props.toolbarIcons.search) {
            if(nextProps.toolbarIcons.search == 'DEFAULT') {
                this.refs.typeahead.getInstance().clear();
            }
        }
    }

    handleChange(e) {
        // If 2 or more characters are entered then make request for suggested names.
        if(e.length >= 2) {
            this.props.getGeonames(e);
        }
        // If one or zero characters are entered then dont provide suggestions
        else {
            // If there are suggestions remove them
            if(this.state.suggestions.length > 0) {
                this.setState({suggestions: []});
            }
        }
    }

    handleEnter(e) {
        this.setState({suggestions: []});
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
                        disabled={this.props.toolbarIcons.search == 'INACTIVE'}
                        options={this.state.suggestions}
                        onChange={this.handleEnter}
                        placeholder={'Search admin boundary or location...'}
                        onInputChange={this.debouncer}
                        labelKey={'name'}
                        paginate={false}
                        emptyLabel={''}
                        minLength={2}
                        renderMenu={(results, menuProps) => {
                            return(
                                <Menu {...menuProps}>
                                    {results.map((result, index) => (
                                        <TypeaheadMenuItem result={result} index={index}/>
                                    ))
                                    }
                                </Menu>        
                            )
                        }}
                    />
                </div>
                <div className={styles.searchAOIButtonContainer}>
                    <SearchAOIButton handleCancel={this.props.handleCancel}/>
                </div>
            </div>
        )
    }
}

SearchAOIToolbar.propTypes = {
    toolbarIcons: React.PropTypes.object,
    geonames: React.PropTypes.object,
    getGeonames: React.PropTypes.func,
    handleSearch: React.PropTypes.func,
    handleCancel: React.PropTypes.func,
    setAllButtonsDefault: React.PropTypes.func,
    setSearchAOIButtonSelected: React.PropTypes.func,
}

function mapStateToProps(state) {
    return {
        geonames: state.geonames,
        toolbarIcons: state.toolbarIcons,
    };
}

function mapDispatchToProps(dispatch) {
    return {
        getGeonames: (query) => {
            dispatch(getGeonames(query));
        },
        setAllButtonsDefault: () => {
            dispatch(setAllButtonsDefault());
        },
        setSearchAOIButtonSelected: () => {
            dispatch(setSearchAOIButtonSelected());
        },
    }
}

export default connect(
    mapStateToProps,
    mapDispatchToProps
)(SearchAOIToolbar);

