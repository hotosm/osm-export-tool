import React, { Component } from "react";
import { ButtonGroup, Row } from "react-bootstrap";
import { FormattedMessage } from "react-intl";
import { connect } from "react-redux";
import { Redirect, Route, Switch } from "react-router";
import { Link, NavLink } from "react-router-dom";
import { Fields, Field } from "redux-form";
import { selectConfigurations } from "../selectors";
import TileSourceField from "./TileSourceField";
import StoredConfigurations from "./StoredConfigurations";
import TreeTagUI from "./TreeTagUI";
import YamlUI from "./YamlUI";
import { REQUIRES_FEATURE_SELECTION, REQUIRES_TILE_SOURCE } from "./utils";
import { renderCheckbox } from "./utils";


class SelectFeatures extends Component {
  render() {
    const {
      configurations,
      exportFormats,
      isClone,
      next,
      onDrop,
      onSearchChange,
      clearSearch,
      onTreeNodeCollapseChange,
      onTreeNodeCheckChange,
      labelFilter,
      tagTreeData
    } = this.props;

    const requiresFeatureSelection = (exportFormats || [])
      .some(x => REQUIRES_FEATURE_SELECTION[x]);

    const requiresTileSource = (exportFormats || [])
      .some(x => REQUIRES_TILE_SOURCE[x]);

    return (


      <Row style={{ height: "auto" }}>
         <Row>
        <Field
            name="unfiltered"
            description="Download all OSM Data - Unfiltered files (Avoid for mbtiles)"
            component={renderCheckbox}
            type="checkbox"
          />
      </Row>

        {requiresFeatureSelection &&
          <ButtonGroup justified>

            <NavLink
              className="btn btn-default"
              to="/exports/new/select/treetag"
            >
              <FormattedMessage
                id="ui.exports.tag_tree"
                defaultMessage="Tag Tree"
              />
            </NavLink>
            <NavLink
              className="btn btn-default"
              to="/exports/new/select/stored"
            >
              <FormattedMessage
                id="ui.exports.stored_configuration"
                defaultMessage="Configs"
              />
            </NavLink>
            <NavLink className="btn btn-default" to="/exports/new/select/yaml">
              <FormattedMessage id="ui.exports.yaml" defaultMessage="YAML" />
            </NavLink>
            {requiresTileSource &&
              <NavLink
                className="btn btn-default"
                to="/exports/new/select/mbtiles"
              >
                <FormattedMessage
                  id="ui.exports.mbtiles"
                  defaultMessage="MBTiles"
                />
              </NavLink>}
          </ButtonGroup>}

        <Row>
          <Switch>
            <Route
              path="/exports/new/select/treetag"
              render={props =>
                <TreeTagUI
                  onSearchChange={onSearchChange}
                  clearSearch={clearSearch}
                  onTreeNodeCollapseChange={onTreeNodeCollapseChange}
                  onTreeNodeCheckChange={onTreeNodeCheckChange}
                  labelFilter={labelFilter}
                  tagTreeData={tagTreeData}
                />}
            />
            <Route
              path="/exports/new/select/stored"
              render={props => <StoredConfigurations />}
            />
            <Route
              path="/exports/new/select/yaml"
              render={props => <YamlUI onDrop={onDrop} />}
            />
            <Route
              path="/exports/new/select/mbtiles"
              render={props =>
                <Fields
                  names={[
                    "mbtiles_maxzoom",
                    "mbtiles_minzoom",
                    "mbtiles_source"
                  ]}
                  component={TileSourceField}
                />}
            />
            <Route
              path="/exports/new/select"
              exact
              render={props => {
                if (requiresFeatureSelection && isClone) {
                  return <Redirect to="/exports/new/select/yaml" />;
                }

                if (requiresFeatureSelection) {
                  return <Redirect to="/exports/new/select/treetag" />;
                }

                return <Redirect to="/exports/new/select/mbtiles" />;
              }}
            />
          </Switch>
        </Row>
        <Row>
          <Link className="btn btn-primary pull-right" to={next}>
            <FormattedMessage id="nav.next" defaultMessage="Next" />
          </Link>
        </Row>
      </Row>
    );
  }
}

const mapStateToProps = state => ({
  configurations: selectConfigurations(state)
});

export default connect(mapStateToProps)(SelectFeatures);
