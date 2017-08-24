import React from "react";
import { ButtonGroup, Row } from "react-bootstrap";
import { FormattedMessage } from "react-intl";
import { Route, Switch } from "react-router";
import { Link, NavLink } from "react-router-dom";

import StoredConfigurations from "./StoredConfigurations";
import TreeTagUI from "./TreeTagUI";
import YamlUI from "./YamlUI";

export default ({
  next,
  onDrop,
  featuresUi,
  setYaml,
  onSearchChange,
  clearSearch,
  onTreeNodeCollapseChange,
  onTreeNodeCheckChange,
  labelFilter,
  tagTreeData
}) =>
  <Row style={{ height: "auto" }}>
    <ButtonGroup justified>
      <NavLink className="btn btn-default" to="/exports/new/select/treetag">
        <FormattedMessage id="ui.exports.tag_tree" defaultMessage="Tag Tree" />
      </NavLink>
      {/* TODO don't display this if no configurations are available */}
      <NavLink className="btn btn-default" to="/exports/new/select/stored">
        <FormattedMessage
          id="ui.exports.stored_configuration"
          defaultMessage="Stored Configuration"
        />
      </NavLink>
      <NavLink className="btn btn-default" to="/exports/new/select/yaml">
        <FormattedMessage id="ui.exports.yaml" defaultMessage="YAML" />
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
      </Switch>
    </Row>
    <Row>
      <Link className="btn btn-primary pull-right" to={next}>
        <FormattedMessage id="nav.next" defaultMessage="Next" />
      </Link>
    </Row>
  </Row>;
