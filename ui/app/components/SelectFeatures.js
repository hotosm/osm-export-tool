import React, { Component } from "react";
import { ButtonGroup, Row } from "react-bootstrap";
import { FormattedMessage } from "react-intl";
import { connect } from "react-redux";
import { Route, Switch } from "react-router";
import { Link, NavLink } from "react-router-dom";
import { Fields } from "redux-form";

import { selectConfigurations } from "../selectors";

import TileSourceField from "./TileSourceField";
import StoredConfigurations from "./StoredConfigurations";
import TreeTagUI from "./TreeTagUI";
import YamlUI from "./YamlUI";

class SelectFeatures extends Component {
  render() {
    const {
      configurations,
      next,
      onDrop,
      onSearchChange,
      clearSearch,
      onTreeNodeCollapseChange,
      onTreeNodeCheckChange,
      labelFilter,
      tagTreeData
    } = this.props;

    return (
      <Row style={{ height: "auto" }}>
        <ButtonGroup justified>
          <NavLink className="btn btn-default" to="/exports/new/select/treetag">
            <FormattedMessage
              id="ui.exports.tag_tree"
              defaultMessage="Tag Tree"
            />
          </NavLink>
          {configurations.length > 0 &&
            <NavLink
              className="btn btn-default"
              to="/exports/new/select/stored"
            >
              <FormattedMessage
                id="ui.exports.stored_configuration"
                defaultMessage="Configs"
              />
            </NavLink>}
          <NavLink className="btn btn-default" to="/exports/new/select/yaml">
            <FormattedMessage id="ui.exports.yaml" defaultMessage="YAML" />
          </NavLink>
          <NavLink className="btn btn-default" to="/exports/new/select/mbtiles">
            <FormattedMessage
              id="ui.exports.mbtiles"
              defaultMessage="MBTiles"
            />
          </NavLink>
        </ButtonGroup>
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
